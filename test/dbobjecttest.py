from seecr.test import SeecrTestCase

from moatley.db import DbObject
from moatley.db.fields import StrField, IntField

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

    def testEquality(self):
        class Mock(DbObject):
            name = StrField("name")
        m1 = Mock(name="Moatley")
        m2 = Mock(name="Moatley")

        self.assertNotEqual(m1, m2)
        self.assertNotEqual(m1.ID, m2.ID)
        m2._values['ID'] = m1._values['ID']
        self.assertEqual(m1, m2)

    def testRepr(self):
        class Mock(DbObject):
            name = StrField("name")
            age = IntField("age")
        m1 = Mock(name="Moatley")
        self.assertEqual("Mock: ID=UUID('{}'), age=0, name='Moatley'".format(m1.ID), repr(m1))

