class DB(object):
    def __init__(self):
        self._registry = {}

    def registerClass(self, *objClasses):
        for objClass in objClasses:
            self._registry[objClass.__name__] = objClass

    def findClass(self, objClassName):
        return self._registry.get(objClassName, None)

    def define(self, objectType, dropIfExists=False):
        raise NotImplementedError()

    def store(self, anObject):
        raise NotImplementedError()

    def delete(self, objectType, identifier):
        raise NotImplementedError()

    def exists(self, objectType, identifier):
        raise NotImplementedError()

    def get(self, objectType, identifier):
        raise NotImplementedError()

    def list(self, objectType, **kwargs):
        raise NotImplementedError()

    def drop(self, objectType):
        raise NotImplementedError()

    def display(self, objectType):
        raise NotImplementedError()
