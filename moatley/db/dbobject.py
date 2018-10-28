from .fields import IDField, findFields

class DbObject(object):
    ID=IDField("ID")

    @classmethod
    def fields(self):
        return findFields(self)

    @classmethod
    def fromWeb(self, **kwargs):
        values = {}
        for field in findFields(self):
            if field.name in kwargs:
                values[field.name] = field.fromWeb(kwargs[field.name])
        return self(**values)

    @property
    def qualifiedId(self):
        return "{}:{}".format(self.__class__.__name__, self.ID)

    def __init__(self, **kwargs):
        self._values = {}
        fields = findFields(self.__class__)
        for field in fields:
            value = kwargs[field.name] if field.name in kwargs else field._defaultValue(self, self.__class__)
            setattr(self, field.name, value)

    def keys(self):
        return [field.name for field in findFields(self.__class__)]

    def __getitem__(self, name):
        if name in self.keys():
            return getattr(self, name) 
        raise KeyError(name)

    def __setitem__(self, name, value):
        if name == "ID":
            raise KeyError("Cannot set ID")

        if name in self.keys():
            setattr(self, name, value)

    def __eq__(self, other): 
        return type(self) == type(other) and dict(self) == dict(other)

    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, ', '.join('{k}={v}'.format(k=i[0], v=repr(i[1])) for i in sorted(dict(self).items())))

    def __hash__(self):
        return hash(repr(self))

    def toWeb(self, **kwargs):
        return {field.name:field.toWeb(getattr(self, field.name)) if field.name not in kwargs else kwargs[field.name](getattr(self,field.name)) for field in findFields(self.__class__)}
