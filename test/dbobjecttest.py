from seecr.test import SeecrTestCase

from moatley.db import DbObject
from moatley.db.fields import StrField, IntField, DecimalField, BooleanField, DateField

from uuid import UUID
from decimal import Decimal
from datetime import datetime

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

    def testFromWeb(self):
        class Mock(DbObject):
            name=StrField("name")
            number=IntField("number")
            dec=DecimalField("dec")
            b1 = BooleanField("b1")
            b2 = BooleanField("b2")
            d1 = DateField("d1")

        m = Mock.fromWeb(name="name", number="10", dec="2.975", b1="1", b2="True", d1="2017-11-30")
        self.assertEqual("name", m.name)
        self.assertEqual(10, m.number)
        self.assertEqual(Decimal(2.975), m.dec)
        self.assertEqual(True, m.b1)
        self.assertEqual(True, m.b2)
        self.assertEqual(datetime.strptime("2017-11-30", "%Y-%m-%d").date(), m.d1)
