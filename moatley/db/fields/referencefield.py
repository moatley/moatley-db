
from .field import Field

class ReferenceField(Field):
    def __init__(self, name):
        super(ReferenceField, self).__init__(name, lambda: None)

    def toWeb(self, value):
        return None if value is None else value.qualifiedId
        
