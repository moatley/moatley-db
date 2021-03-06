from .field import Field

class BooleanField(Field):
    def __init__(self, name):
        super(BooleanField, self).__init__(name, bool)

    def fromWeb(self, value):
        return value == "True" or value == "1"
