from .field import Field

class _Container(list):
    pass

class CollectionField(Field):
    def __init__(self, name):
        super(CollectionField, self).__init__(name, _Container)
