import unittest
from app import create_app, db
from app.models import Post, Tag, Category


class CreateCateTagTest(unittest.TestCase):
    """测试基本的创建分类和标签"""

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_add_category(self):
        """测试创建分类"""
        cate = Category(name='hello world')
        db.session.add(cate)
        db.session.commit()
        self.assertTrue(Category.query.filter_by(name='hello world').first is not None)

    def test_02_generate_category(self):
        """测试批量创建分类"""
        Category.generate_fake(20)
        self.assertTrue(Category.query.count() == 20)

    def test_03_category_name(self):
        """测试分类名称中不能包含反斜杠/"""
        self.assertRaises(AttributeError, lambda: Category(name='hello/world'))

    def test_04_category_link(self):
        """测试分类link中替代分类名称的空格为下划线"""
        cate = Category(name='hello world')
        self.assertTrue(cate.link == 'hello_world')

    def test_05_category_family(self):
        """测试分类层级关系"""
        cate1 = Category(name='cate1')
        db.session.add(cate1)
        db.session.commit()

        cate2 = Category(name='cate2')
        cate2.parent = cate1
        db.session.add(cate2)
        db.session.commit()

        cate3 = Category(name='cate3')
        cate3.parent = cate2
        db.session.add(cate3)
        db.session.commit()

        self.assertTrue(cate2 in cate1.children.all() and
                        cate2.link == 'cate1/cate2' and
                        cate3 in cate2.children.all() and
                        cate3.link == 'cate1/cate2/cate3' and
                        cate1.parent is None)

    def test_06_rename_category(self):
        """测试分类改名"""
        cate1 = Category(name='cate1')
        db.session.add(cate1)
        db.session.commit()

        cate2 = Category(name='cate2')
        cate2.parent = cate1
        db.session.add(cate2)
        db.session.commit()

        cate3 = Category(name='cate3')
        cate3.parent = cate2
        db.session.add(cate3)
        db.session.commit()

        p = Post()
        Post.publish(post=p,
                     title='post',
                     content='post',
                     category=cate2)

        cate1.name = 'cate11'
        cate2.name = 'cate222'

        self.assertTrue(cate2 in cate1.children.all() and
                        cate2.link == 'cate11/cate222' and
                        cate3 in cate2.children.all() and
                        cate3.link == 'cate11/cate222/cate3' and
                        cate3.level == 2 and
                        cate3.parent == cate2 and
                        cate2.posts_count == 1 and
                        cate1.posts_count == 1 and
                        cate3.posts_count == 0)

    def test_07_order_cate(self):
        """测试分类顺序"""
        cate1 = Category(name='cate1')
        db.session.add(cate1)
        db.session.commit()

        cate2 = Category(name='cate2',
                         order=1)
        cate3 = Category(name='cate3',
                         order=2)
        cate3.parent = cate1
        cate2.parent = cate1
        db.session.add(cate2)
        db.session.add(cate3)
        db.session.commit()

        self.assertTrue(cate2.order < cate3.order)

    def test_08_add_tag(self):
        """测试新建标签"""
        tag = Tag(name='hello world')
        db.session.add(tag)
        db.session.commit()
        self.assertTrue(Tag.query.filter_by(name='hello world').first is not None)

    def test_09_generate_tag(self):
        """测试批量新建标签"""
        Tag.generate_fake(20)
        self.assertTrue(Tag.query.count() == 20)

    def test_10_tag_link(self):
        """测试标签link中替代标签名称的空格为下划线"""
        tag = Tag(name='hello world')
        self.assertTrue(tag.link == 'hello_world')
