from seecr.test import SeecrTestCase, CallTrace

from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from moatley.db import Mysql, DbObject
from moatley.db.fields import StrField, IntField, DateField, IDField, ReferenceField, CollectionField, DecimalField, BooleanField, TextField

class Mock(DbObject):
    name = StrField("name")
    age = IntField("age")
    dob = DateField("dob")
    weight = DecimalField("weight")
    description = TextField("description")

class MysqlTest(SeecrTestCase):
    def setUp(self):
        super(MysqlTest, self).setUp()
        self.db = Mysql(username="test", password="test", database="test", verbose=False)
        self.db.drop(Mock)
        self.db.define(Mock)

    def testCreatedTable(self):
        self.assertEqual(set([
            ('dob', DateField), 
            ('age', IntField), 
            ('name', StrField), 
            ('ID', IDField),
            ('weight', DecimalField),
            ('description', TextField)]), set(self.db.display(Mock)))

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
            number=IntField("number")
        class Book(DbObject):
            title=StrField("title")
            pages=CollectionField("pages")

        self.db.define(Book, dropIfExists=True)
        self.db.registerClass(Book)
        self.db.define(Page, dropIfExists=True)
        self.db.registerClass(Page)

        b = Book(title="My book")

        p1 = Page(number=1)
        p2 = Page(number=2)

        b.pages.append(p1)
        b.pages.append(p2)

        self.assertEquals(2, len(b.pages))

        self.db.store(b)

        b1 = self.db.get(Book, b.ID)
        self.assertEqual(2, len(b1.pages))

        p3 = Page(number=3)
        b1.pages.append(p3)
        self.db.store(b1)

        self.assertEqual(3, len(list(self.db.list(Page))))

    def testCollectionContained(self):
        class Page(DbObject):
            number=IntField("number")
        class Book(DbObject):
            title=StrField("title")
            pages=CollectionField("pages")
        self.db.define(Page, dropIfExists=True)
        self.db.registerClass(Page)
        self.db.define(Book, dropIfExists=True)
        self.db.registerClass(Book)

        b = Book(title="My book")

        p1 = Page(number=1)
        b.pages.append(p1)
        self.db.store(b)
        self.assertEqual(1, len(list(self.db.list(Page))))

        b.pages.remove(p1)
        self.assertEqual([], b.pages)
        self.db.store(b)
        self.assertEqual(0, len(list(self.db.list(Page))))

    def testCollectionNotContained(self):
        class Page(DbObject):
            number=IntField("number")
        class Book(DbObject):
            title=StrField("title")
            pages=CollectionField("pages", contained=False)
        self.db.registerClass(Page, Book)
        self.db.define(Page, dropIfExists=True)
        self.db.define(Book, dropIfExists=True)

        b = Book(title="My book")

        p1 = Page(number=1)
        self.db.store(p1)
        self.assertEquals([p1], list(self.db.list(Page)))

        b.pages.append(p1)
        self.db.store(b)
        self.assertEqual(1, len(list(self.db.list(Page))))

        b.pages.remove(p1)
        self.assertEqual([], b.pages)
        self.assertEquals([p1], list(self.db.list(Page)))
        self.db.store(b)
        self.assertEquals([p1], list(self.db.list(Page)))


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
        b = Book(price=16.0/7)
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

    def testTextField(self):
        class Book(DbObject):
            text=TextField("text")
        self.db.define(Book, dropIfExists=True)
        b = Book(text='\n'.join("Line {}".format(i) for i in range(10)))
        self.db.store(b)
        
        b1 = self.db.get(Book, b.ID)
        self.assertEqual('\n'.join("Line {}".format(i) for i in range(10)), b1.text)

    def testReferenceField(self):
        class Book(DbObject):
            author=ReferenceField("author")
        self.db.define(Book, dropIfExists=True)
        b = Book()
        self.assertEqual(None, b.author)
        self.db.store(b)

        b1 = self.db.get(Book, b.ID)
        self.assertEqual(None, b1.author)



