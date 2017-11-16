from .fields import IDField, findFields

class DbObject(object):
    ID=IDField("ID")

    @property
    def qualifiedId(self):
        return "{}:{}".format(self.__class__.__name__, self.ID)

    def __init__(self, **kwargs):
        self._values = {}
        fields = findFields(self.__class__)
        for field in fields:
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])

    def keys(self):
        return [field.name for field in findFields(self.__class__)]

    def __getitem__(self, name):
        if name in self.keys():
            return getattr(self, name) 
        raise KeyError(name)

