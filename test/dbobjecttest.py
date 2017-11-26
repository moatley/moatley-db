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

    def testSetItem(self):
        class Mock(DbObject):
            name = StrField("name")

        m = Mock()
        m['name'] = 'Johan'

        self.assertEqual("Johan", m.name)
        try:
            m['ID'] = "Nope can't do"
            self.fail("Cannot set ID")
        except KeyError, e:
            self.assertEqual("'Cannot set ID'", str(e))

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

    def testFields(self):
        class Mock(DbObject):
            name = StrField("name")
            age = IntField("age")
        self.assertEqual(set(['age', 'name', 'ID']), set([f.name for f in Mock.fields()]))

