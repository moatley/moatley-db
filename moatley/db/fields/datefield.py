from datetime import datetime
from .field import Field

class DateField(Field):
    def __init__(self, name):
        super(DateField, self).__init__(name, lambda: datetime.now().date())

    def fromWeb(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()
