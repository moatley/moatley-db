from .fields import Field, IntField, StrField, DateField, IDField, CollectionField, findFields

from os.path import isdir, join, abspath, isfile
from shutil import rmtree
from os import makedirs, listdir
from seecr.tools import atomic_write
from simplejson import dump, load
from datetime import datetime
from uuid import UUID

db_transformations = {
    IDField : {
        "to": lambda v: str(v),
        "from": lambda v: UUID(v)},
    DateField: {
        "to": lambda v: v.isoformat(),
        "from": lambda v: datetime.strptime(v, '%Y-%m-%d').date()}
}


class Json(object):
    def __init__(self, root):
        self._root = abspath(root)

    def define(self, objectType, dropIfExists=False):
        objectDir = join(self._root, objectType.__name__)
        if isdir(objectDir) and dropIfExists:
            self.drop(objectType)
        makedirs(objectDir)

    def store(self, anObject):
        objectDir = join(self._root, anObject.__class__.__name__)
        with atomic_write(join(objectDir, str(anObject.ID))) as fp:
            dump({field.name:db_transformations[type(field)]['to'](getattr(anObject, field.name)) if type(field) in db_transformations else getattr(anObject, field.name) for field in findFields(anObject.__class__)}, fp)


    def delete(self, objectType, identifier):
        pass

    def exists(self, objectType, identifier):
        objectDir = join(self._root, objectType.__name__)
        return isfile(join(objectDir, str(identifier)))

    def get(self, objectType, identifier):
        return self._loadJsonFile(objectType, identifier) if self.exists(objectType, str(identifier)) else None

    def _loadJsonFile(self, objectType, identifier):
        objectDir = join(self._root, objectType.__name__)
        values = load(open(join(objectDir, str(identifier))))
        fields = {f.name:type(f) for f in findFields(objectType)}
        obj = objectType()
        for name in values:
            value = db_transformations[fields[name]]["from"](values[name]) if fields[name] in db_transformations else values[name]
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

    def display(self, objectType):
        pass
