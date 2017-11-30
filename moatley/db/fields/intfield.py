from .field import Field

class IntField(Field):
    def __init__(self, name):
        super(IntField, self).__init__(name, int)

    def fromWeb(self, value):
        return int(value)
