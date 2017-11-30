from seecr.test import SeecrTestCase, CallTrace

from uuid import uuid4
from decimal import Decimal
from datetime import datetime
from moatley.db import Json, DbObject
from moatley.db.fields import StrField, IntField, DateField, IDField, ReferenceField, CollectionField, ReferenceField, DecimalField, BooleanField


class Mock(DbObject):
    name = StrField("name")
    age = IntField("age")
    dob = DateField("dob")

class JsonTest(SeecrTestCase):
    def setUp(self):
        super(JsonTest, self).setUp()
        self.db = Json(root=self.tempdir)
        self.db.drop(Mock)
        self.db.define(Mock)


    def unused_testCreatedTable(self):
        self.assertEqual([
            ('dob', DateField), 
            ('age', IntField), 
            ('name', StrField), 
            ('ID', IDField)], list(self.db.display(Mock)))

    def testSetOnCreate(self):
        m = Mock(name="John", age=12)
        self.assertEqual("John", m.name)
        self.assertEqual(12, m.age)

    def testStoreAndGet(self):
        m = Mock()
        self.assertEqual("", m.name)
        self.assertEqual(0, m.age)
        self.assertEqual(datetime.now().date(), m.dob)
        
        self.db.store(m)

        n = self.db.get(Mock, m.ID)
        self.assertEqual("", n.name)
        self.assertEqual(0, n.age)
        self.assertEqual(datetime.now().date(), n.dob)
        self.assertEqual(m.ID, n.ID)


    def testChanges(self):
        m = Mock(name="John Doe")
        self.db.store(m)
        n = self.db.get(Mock, m.ID)
        self.assertEqual("John Doe", n.name)
        
        m.name = "Jane Smith"
        self.db.store(m)
        n = self.db.get(Mock, m.ID)
        self.assertEqual("Jane Smith", n.name)


    def testList(self):
        m1 = Mock(name="John Smith")
        self.db.store(m1)
        m2 = Mock(name="Jane Doe")
        self.db.store(m2)

        allMocks = list(self.db.list(Mock))
        self.assertEqual(2, len(allMocks))

        allMocks = list(self.db.list(Mock, name="Jane Doe"))
        self.assertEqual(1, len(allMocks))
        self.assertEqual([], list(self.db.list(Mock, name="Jane Doe", age=15)))

    def testCollectionAdd(self):
        class Page(DbObject):
            book=StrField("book")
            number=IntField("number")
        class Book(DbObject):
            title=StrField("title")
            pages=CollectionField("pages", Page, "book")
        self.db.registerClass(Book, Page)

        self.db.define(Book, dropIfExists=True)
        self.db.define(Page, dropIfExists=True)

        b = Book(title="My book")

        p1 = Page(number=1)
        p2 = Page(number=2)

        b.pages.append(p1)
        b.pages.append(p2)

        self.assertEquals(2, len(b.pages))
        self.assertEquals("Book:{}".format(b.ID), p1.book)
        self.assertEquals("Book:{}".format(b.ID), p2.book)

        self.db.store(b)

        b1 = self.db.get(Book, b.ID)
        self.assertEqual(2, len(b1.pages))

        p3 = Page(number=3)
        b1.pages.append(p3)
        self.db.store(b1)

        self.assertEqual(3, len(list(self.db.list(Page))))

    def testCollectionContained(self):
        class Page(DbObject):
            book=StrField("book")
            number=IntField("number")
        class Book(DbObject):
            title=StrField("title")
            pages=CollectionField("pages", Page, "book")
        self.db.registerClass(Book, Page)
        self.db.define(Page, dropIfExists=True)
        self.db.define(Book, dropIfExists=True)

        b = Book(title="My book")

        p1 = Page(number=1)
        b.pages.append(p1)
        self.db.store(b)
        self.assertEqual(1, len(list(self.db.list(Page))))

        b.pages.remove(p1)
        self.assertEqual([], b.pages)
        self.db.store(b)
        self.assertEqual(0, len(list(self.db.list(Page))))

    def testReferenceField(self):
        class Book(DbObject):
            title=StrField("title")
        class Page(DbObject):
            book=ReferenceField("book")
            number=IntField("number")

        self.db.define(Page, dropIfExists=True)
        self.db.registerClass(Page)
        self.db.define(Book, dropIfExists=True)
        self.db.registerClass(Book)

        b = Book(title="The answer")
        p = Page(number=1, book=b)

        self.db.store(b)
        self.db.store(p)

        revisitedPage = self.db.get(Page, p.ID)
        self.assertEqual(b, revisitedPage.book)

    def testDecimalField(self):
        class Book(DbObject):
            price=DecimalField("price")

        self.db.define(Book, dropIfExists=True)
        b = Book(price=Decimal(16.0/7))
        self.db.store(b)

        b1 = self.db.get(Book, b.ID)
        self.assertEquals(b.price, b1.price)
        self.assertEqual(Decimal, type(b1.price))

    def testBooleanField(self):
        class Book(DbObject):
            fiction=BooleanField("fiction")
        self.db.define(Book, dropIfExists=True)
        b = Book(fiction=True)
        self.db.store(b)
        
        b1 = self.db.get(Book, b.ID)
        self.assertEquals(b.fiction, b1.fiction)
        self.assertEqual(bool, type(b1.fiction))

        b2 = Book()
        self.assertFalse(b2.fiction)
