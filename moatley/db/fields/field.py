class Field(object):
    def __init__(self, name, type):
        self._name = name
        self._type = type

    @property
    def name(self):
        return self._name

    def _defaultValue(self, owner, ownerType):
        return self._type()

    def __get__(self, owner, ownerType):
        if not self._name in owner._values:
            owner._values[self._name] = self._defaultValue(owner, ownerType)
        return owner._values[self._name]

    def __set__(self, owner, value):
        owner._values[self._name] = value

