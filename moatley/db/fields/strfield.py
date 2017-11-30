from .field import Field

class StrField(Field):
    def __init__(self, name):
        super(StrField, self).__init__(name, str)

    def fromWeb(self, value):
        return str(value)

