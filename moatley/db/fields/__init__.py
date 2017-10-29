from field import Field

from strfield import StrField
from intfield import IntField
from idfield import IDField
from datefield import DateField
from referencefield import ReferenceField
from collectionfield import CollectionField

def findFields(oType):
    def _findFields(oType, results):
        if oType == object:
            return
        results.extend([v for _,v in oType.__dict__.items() if isinstance(v, Field)])
        for sType in oType.__bases__:
            _findFields(sType, results)
    results = []
    _findFields(oType, results)
    return results
