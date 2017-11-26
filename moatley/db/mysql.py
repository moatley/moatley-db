from MySQLdb import Connect, OperationalError, escape_string
from .fields import Field, IntField, StrField, DateField, IDField, CollectionField, ReferenceField, findFields, DecimalField
from .cursor import Cursor

from datetime import datetime
from uuid import UUID

from db import DB

db_transformations = {
    IntField: {
        "to": lambda v, *args: v,
        "from": lambda v, *args: v},
    StrField: {
        "to": lambda v, *args: escapeIfNeeded(v),
        "from": lambda v, *args: v},
    IDField: {
        "to": lambda v, *args: escapeIfNeeded(str(v)),
        "from": lambda v, *args: UUID(v)},
    DateField: {
        "to": lambda v, *args: escapeIfNeeded(str(v)),
        "from": lambda v, *args: v},
    ReferenceField: {
        "to": lambda v, *args: escapeIfNeeded(v.qualifiedId),
        "from": lambda v, db, *args: db.get(*v.split(":", 1))},
    DecimalField: {
        "to": lambda v, *args: float(v),
        "from": lambda v, *args: v},

}

db_types = {
    IntField: "INT(11)",
    StrField: "VARCHAR(255)",
    IDField: "VARCHAR(36)",
    DateField: "DATE",
    ReferenceField: "VARCHAR(72)",
    DecimalField: lambda field: "DECIMAL({},{})".format(field.fractionLength*2, field.fractionLength)
}

def getDbType(field):
    r = db_types.get(field.__class__)
    if callable(r):
        r = r(field)
    return r

def escapeIfNeeded(value):
    return '"{}"'.format(escape_string(value)) if type(value) == str else value

def to_db(field, value, *args):
    return db_transformations[field.__class__]['to'](value, *args) if field.__class__ in db_transformations else value

def from_db(field, value, *args):
    return db_transformations[field.__class__]['from'](value, *args) if field.__class__ in db_transformations else value

class Mysql(DB):
    def __init__(self, username, password, database, verbose=False):
        super(Mysql, self).__init__()
        self._username = username
        self._password = password
        self._database = database
        self._db = None
        self._verbose = verbose

        self.connect()

    def connect(self):
        if self._db is None or self._db.cqlstate != "000000":
            self._db = Connect(user=self._username, passwd=self._password, db=self._database)

    def define(self, objectType, dropIfExists=False):
        tables = [each[0] for each in self._sql("show tables")]
        if objectType.__name__ in tables:
            if dropIfExists:
                self.drop(objectType)
            else:
                return
        
        fields = [field for field in findFields(objectType) if type(field) in db_types]
        idFields = [field for field in fields if type(field) == IDField]

        stmt = """
        CREATE TABLE `{tableName}` ( 
            {fields}, 
            PRIMARY KEY({idFields}) 
        ) ENGINE=MyISAM""".format(
            tableName=objectType.__name__,
            fields=','.join('`{name}` {sqlType}'.format(name=field.name, sqlType=getDbType(field)) 
                for field in fields),
            idFields=','.join('`{}`'.format(field._name) 
                for field in idFields))

        for result in self._sql(stmt):
            pass

    def store(self, anObject):
        objectType = anObject.__class__
        
        allFields = findFields(objectType)
        fields = [field for field in allFields if type(field) in db_types]
        collections = [field for field in allFields if type(field) == CollectionField]
        identifier = anObject.ID

        fieldStatement = ','.join('`{name}`={value}'.format(
                    name=field.name, 
                    value=to_db(field, getattr(anObject, field.name), self)) for field in fields)
        
        if not self.exists(objectType, identifier):
            stmt = "INSERT INTO `{tableName}` SET {fields}".format(
                tableName=objectType.__name__,
                fields=fieldStatement)
        else:
            idFields = [field for field in fields if type(field) == IDField]
            fields = [field for field in fields if type(field) != IDField]
            stmt = "UPDATE `{tableName}` SET {fields} WHERE {idField}={identifier}".format(
                tableName=objectType.__name__,
                fields=fieldStatement,
                idField=idFields[0].name,
                identifier=to_db(idFields[0], identifier))

        for result in self._sql(stmt):
            pass

        for collection in collections:
            items = getattr(anObject, collection.name)
            for item in items:
                self.store(item)
            storedItems = set([obj.ID for obj in self.list(collection.remoteObjectType, **{collection._reference: anObject.qualifiedId})])
            itemIDs = set([item.ID for item in items])

            for item in storedItems.difference(itemIDs):
                self.delete(collection.remoteObjectType, item)

    def delete(self, objectType, identifier):
        fields = findFields(objectType)
        idFields = [field for field in fields if type(field) == IDField]
        stmt = "DELETE FROM `{tableName}` WHERE {idField}={identifier}".format(
            tableName=objectType.__name__,
            idField=idFields[0].name,
            identifier=to_db(idFields[0], identifier))
        for result in self._sql(stmt):
            pass

    def exists(self, objectType, identifier):
        fields = findFields(objectType)
        idFields = [field for field in fields if type(field) == IDField]
        stmt = "SELECT COUNT(*) from `{tableName}` WHERE {idField}={identifier}".format(
            tableName=objectType.__name__,
            idField=idFields[0].name,
            identifier=to_db(idFields[0], identifier))
        for result in self._sql(stmt):
            return result[0] > 0

    def get(self, objectType, identifier):
        if type(objectType) is str:
            errorText = "No class named '{}' registered".format(objectType)
            objectType = self.findClass(objectType)
            if objectType is None:
                raise ValueError(errorText)

        allFields = findFields(objectType)
        fields = [field for field in allFields if type(field) in db_types]
        idFields = [field for field in fields if type(field) == IDField]
        stmt = "SELECT {fieldNames} FROM `{tableName}` WHERE {idField}={identifier}".format(
            fieldNames=','.join('`{}`'.format(field.name) for field in fields),
            tableName=objectType.__name__,
            idField=idFields[0].name,
            identifier=to_db(idFields[0], identifier))
     
        collectionFields = [field for field in allFields if type(field) == CollectionField]
        for obj in self._loadFromSelect(stmt, objectType, fields, collectionFields):
            return obj

    def list(self, objectType, **kwargs):
        allFields = findFields(objectType)
        fields = [field for field in allFields if type(field) in db_types]
        stmt = "SELECT {fieldNames} FROM `{tableName}`".format(
            fieldNames=','.join('`{}`'.format(field.name) for field in fields),
            tableName=objectType.__name__)

        if kwargs:
            fieldNames = {f.name:f for f in findFields(objectType)}
            queryFields = [(fieldNames[k], v) for k,v in kwargs.items() if k in fieldNames]
            stmt = "{stmt} WHERE {fields}".format(
                stmt=stmt,
                fields=' AND '.join('`{name}`={value}'.format(
                    name=field.name, 
                    value=to_db(field, value)) for (field, value) in queryFields))

        collectionFields = [field for field in allFields if type(field) == CollectionField]
        for obj in self._loadFromSelect(stmt, objectType, fields, collectionFields):
            yield obj

    def _loadFromSelect(self, stmt, objectType, fields, collections):
        for result in self._sql(stmt):
            obj = objectType()
            for n, field in enumerate(fields):
                setattr(obj, field.name, from_db(field, result[n], self))
            for collection in collections:
                values = list(self.list(collection.remoteObjectType, **{collection._reference: obj.qualifiedId}))
                setattr(obj, collection.name, values)
            yield obj

    def drop(self, objectType):
        for i in self._sql("DROP TABLE IF EXISTS `{}`".format(objectType.__name__)):
            pass

    def display(self, objectType):
        fields = {f.name:f for f in findFields(objectType)}
        for i in self._sql("DESCRIBE `{}`".format(objectType.__name__)):
            name, dbType, mayBeNull, key, default, _ = i
            yield name, fields[name].__class__

    def _sql(self, statement):
        if self._verbose:
            print statement
        with Cursor(self._db) as cursor:
            result = cursor.execute(statement)
            for n in range(result):
                yield cursor.fetchone()


