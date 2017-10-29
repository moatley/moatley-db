from uuid import uuid4
from .field import Field

class IDField(Field):
    def __init__(self, name):
        super(IDField, self).__init__(name, uuid4)

