from .field import Field

class TextField(Field):
    def __init__(self, name):
        super(TextField, self).__init__(name, str)

    def fromWeb(self, value):
        return str(value)


