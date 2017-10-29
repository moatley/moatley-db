from .field import Field

class CollectionProxy(list):

    def __init__(self, owner, reference, *args, **kwargs):
        super(CollectionProxy, self).__init__(*args, **kwargs)
        self._owner = owner
        self._reference = reference

    def append(self, item):
       setattr(item, self._reference, self._owner.qualifiedId)
       super(CollectionProxy, self).append(item)


class CollectionField(Field):
    def __init__(self, name, remoteObjectType, reference):
        super(CollectionField, self).__init__(name, CollectionProxy)
        self._remoteObjectType = remoteObjectType
        self._reference = reference

    @property
    def remoteObjectType(self):
        return self._remoteObjectType

    def _defaultValue(self, owner, ownerType):
        return self._type(owner, self._reference)

    def __set__(self, owner, value):
        proxy = CollectionProxy(owner, self._reference)
        proxy.extend(value)

        super(CollectionField, self).__set__(owner, proxy)
