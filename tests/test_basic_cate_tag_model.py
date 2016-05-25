import unittest
from app import create_app, db
from app.models import Post, Category, Tag


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_category(self):
        cate = Category(name='hello world')
        db.session.add(cate)
        db.session.commit()
        self.assertTrue(Category.query.filter_by(name='hello world').first is not None)

    def test_generate_category(self):
        Category.generate_fake(20)
        self.assertTrue(Category.query.count() == 20)

    def test_category_name(self):
        self.assertRaises(AttributeError, lambda: Category(name='hello/world'))

    def test_category_link(self):
        cate = Category(name='hello world')
        self.assertTrue(cate.link == 'hello_world')

    def test_add_tag(self):
        tag = Tag(name='hello world')
        db.session.add(tag)
        db.session.commit()
        self.assertTrue(Tag.query.filter_by(name='hello world').first is not None)

    def test_generate_tag(self):
        Tag.generate_fake(20)
        self.assertTrue(Tag.query.count() == 20)

    def test_tag_link(self):
        tag = Tag(name='hello world')
        self.assertTrue(tag.link == 'hello_world')
