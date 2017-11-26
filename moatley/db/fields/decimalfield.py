from .field import Field
from decimal import Decimal

class DecimalField(Field):
    def __init__(self, name, fractionLength=10):
        super(DecimalField, self).__init__(name, Decimal)
        self._fractionLength = fractionLength

    @property
    def fractionLength(self):
        return self._fractionLength

    def __set__(self, owner, value):
        super(DecimalField, self).__set__(owner, Decimal(round(value, self._fractionLength)))
