from .fields import Field, IntField, StrField, DateField, IDField, CollectionField, findFields
from .db import DB

from os.path import isdir, join, abspath, isfile
from shutil import rmtree
from os import makedirs, listdir, remove
from seecr.tools import atomic_write
from simplejson import dump, load
from datetime import datetime
import sys
from uuid import UUID

db_transformations = {
    IDField : {
        "to": lambda v, *args: str(v),
        "from": lambda v, *args: UUID(v)},
    DateField: {
        "to": lambda v, *args: v.isoformat(),
        "from": lambda v, *args: datetime.strptime(v, '%Y-%m-%d').date()},
    CollectionField: {
        "to": lambda v, db: [db.store(o) for o in v],
        "from": lambda v, db: [db.get(objType, identifier) for objType, identifier in (i.split(":",1) for i in v)]},
}


class Json(DB):
    def __init__(self, root):
        super(Json, self).__init__()
        self._root = abspath(root)

    def define(self, objectType, dropIfExists=False):
        objectDir = join(self._root, objectType.__name__)
        if isdir(objectDir) and dropIfExists:
            self.drop(objectType)
        makedirs(objectDir)

    def store(self, anObject):
        objectDir = join(self._root, anObject.__class__.__name__)
        itemsToDelete = []
        if self.exists(anObject.__class__, anObject.ID):
            storedObject = self.get(anObject.__class__, anObject.ID)
            collectionFields = [f for f in findFields(anObject.__class__) if type(f) is CollectionField]
            for collectionField in collectionFields:
                storedItems = getattr(storedObject, collectionField.name)
                currentItems = getattr(anObject, collectionField.name)
                itemsToDelete.extend(set(storedItems).difference(currentItems))

        with atomic_write(join(objectDir, str(anObject.ID))) as fp:
            dump({field.name:db_transformations[type(field)]['to'](getattr(anObject, field.name), self) if type(field) in db_transformations else getattr(anObject, field.name) for field in findFields(anObject.__class__)}, fp)

        if len(itemsToDelete) > 0:
            for item in itemsToDelete:
                self.delete(item.__class__, item.ID)
        return anObject.qualifiedId

    def delete(self, objectType, identifier):
        if self.exists(objectType, identifier):
            remove(join(self._root, objectType.__name__, str(identifier)))

    def exists(self, objectType, identifier):
        return isfile(join(self._root, objectType.__name__, str(identifier)))

    def get(self, objectType, identifier):
        if type(objectType) is str:
            errorText = "No class named '{}' registered".format(objectType)
            objectType = self.findClass(objectType)
            if objectType is None:
                raise ValueError(errorText)
        result = self._loadJsonFile(objectType, identifier) if self.exists(objectType, str(identifier)) else None
        return result

    def _loadJsonFile(self, objectType, identifier):
        objectDir = join(self._root, objectType.__name__)
        values = load(open(join(objectDir, str(identifier))))
        fields = {f.name:f for f in findFields(objectType)}
        obj = objectType()
        for name in values:
            fieldType = type(fields[name])
            value = db_transformations[fieldType]["from"](values[name], self) if fieldType in db_transformations else values[name]
            setattr(obj, name, value)
        return obj


    def list(self, objectType, **kwargs):
        objectDir = join(self._root, objectType.__name__)
        for fname in listdir(objectDir):
            obj = self._loadJsonFile(objectType, fname)
            match = True
            for name, value in kwargs.items():
                if getattr(obj, name) != value:
                    match = False
                    break
            if match:
                yield obj

    def drop(self, objectType):
        objectDir = join(self._root, objectType.__name__)
        if isdir(objectDir):
            rmtree(objectDir)
