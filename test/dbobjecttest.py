from seecr.test import SeecrTestCase

from moatley.db import DbObject
from moatley.db.fields import StrField

from uuid import UUID

class DbObjectTest(SeecrTestCase):
    def testAccessAsDictionary(self):
        class Mock(DbObject):
            name = StrField("name")

        m = Mock(name="Moatley")
        self.assertEquals("Moatley", m['name'])
        self.assertTrue(type(m['ID']) is UUID, m['ID'])
        self.assertRaises(KeyError, lambda: m['no such thing'])
        try:
            m['name'] = "Nope can't do"
            self.fail("Shouldnt be able to set with item assignment")
        except TypeError, e:
            self.assertEqual("'Mock' object does not support item assignment", str(e))
