import unittest
from app import create_app, db
from app.models import Post, Tag, Category


class BlogOperationTest(unittest.TestCase):
    """测试基本的创建分类和标签"""

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_move_cate(self):
        """测试移动分类"""
        cate3 = Category.query.filter_by(_name='cate3').first()
        p = Post()
        Post.publish(post=p,
                     title='post',
                     content='post',
                     category=cate3)

        cate1 = Category.query.filter_by(_name='cate1').first()
        cate3.parent = cate1
        db.session.commit()
        cate2 = Category.query.filter_by(_name='cate2').first()

        self.assertTrue(p._category == 'cate1/cate3' and
                        cate1.children.count() == 2 and
                        cate3.link == 'cate1/cate3' and
                        cate1.posts_count == 1 and
                        cate2.posts_count == 0)

    def test_02_batch_move_cate(self):
        """测试批量移动分类"""
        cate1 = Category.query.filter_by(_name='cate1').first()
        cate2 = Category.query.filter_by(_name='cate2').first()
        cate3 = Category.query.filter_by(_name='cate3').first()

        cate4 = Category(name='cate4')
        db.session.add(cate4)
        db.session.commit()
        p1 = Post()
        Post.publish(post=p1,
                     title='post1',
                     content='post1',
                     category=cate3)

        p2 = Post()
        Post.publish(post=p2,
                     title='post2',
                     content='post2',
                     category=cate4)

        Category.move('cate5', [3, 4])
        cate5 = Category.query.filter_by(_name='cate5').first()

        self.assertTrue(p1._category == 'cate5/cate3' and
                        p2._category == 'cate5/cate4' and
                        cate5.posts_count == 2 and
                        cate2.posts_count == 0 and
                        cate3.parent == cate4.parent == cate5)

    def test_03_merge_cate(self):
        """测试合并分类"""
        cate1 = Category.query.filter_by(_name='cate1').first()
        cate2 = Category.query.filter_by(_name='cate2').first()
        cate3 = Category.query.filter_by(_name='cate3').first()

        p1 = Post()
        Post.publish(post=p1,
                     title='post1',
                     content='post1',
                     category=cate3)

        p2 = Post()
        Post.publish(post=p2,
                     title='post2',
                     content='post2',
                     category=cate2)

        Category.marge('new cate', [cate3.id, cate2.id])
        new_cate = Category.query.filter_by(_name='new cate').first()
        self.assertTrue(cate1.children.count() == 0 and
                        new_cate.posts_count == 2 and
                        p1.category.link == new_cate.link and
                        p2.category.link == new_cate.link and
                        Category.query.count() == 2)

    def test_04_merge_cate_to_default(self):
        """测试合并分类到默认分类"""
        cate1 = Category.query.filter_by(_name='cate1').first()
        cate2 = Category.query.filter_by(_name='cate2').first()
        cate3 = Category.query.filter_by(_name='cate3').first()

        p1 = Post()
        Post.publish(post=p1,
                     title='post1',
                     content='post1',
                     category=cate3)

        p2 = Post()
        Post.publish(post=p2,
                     title='post2',
                     content='post2',
                     category=cate2)
        Category.marge('cate1', [cate3.id, cate2.id, cate1.id])
        self.assertTrue(cate1.children.count() == 0 and
                        cate1.posts_count == 2 and
                        Category.query.count() == 1 and
                        p1.category == cate1 and
                        p2.category == cate1)

    def test_05_delete_cate(self):
        """测试删除分类"""
        cate1 = Category.query.filter_by(_name='cate1').first()
        cate2 = Category.query.filter_by(_name='cate2').first()
        cate3 = Category.query.filter_by(_name='cate3').first()

        p = Post()
        Post.publish(post=p,
                     title='post1',
                     content='post1',
                     category=cate3)

        Category.delete(cate2)

        self.assertTrue(Category.query.count() == 2 and
                        p.category == cate3 and
                        cate3.parent == cate1 and
                        cate1.posts_count == 1)

    def test_06_delete_default_cate(self):
        """测试删除默认分类"""
        cate1 = Category.query.get(1)

        self.assertRaises(AttributeError, lambda: Category.delete(cate1))

    def test_07_delete_tag(self):
        """测试删除标签"""
        tag1 = Tag(name='tag1')
        tag2 = Tag(name='tag2')
        tag3 = Tag(name='tag3')

        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()

        p = Post()
        Post.publish(post=p,
                     title='post1',
                     content='post1',
                     tags='tag1, tag2, tag3')

        Tag.delete(tag3)

        self.assertTrue(Tag.query.count() == 2 and
                        p.tags == ['tag1', 'tag2'] and
                        tag1.posts_count == 1 and
                        tag2.posts_count == 1)

    def test_08_merge_tag(self):
        """测试合并标签"""
        tag1 = Tag(name='tag1')
        tag2 = Tag(name='tag2')
        tag3 = Tag(name='tag3')

        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()

        p = Post()
        Post.publish(post=p,
                     title='post1',
                     content='post1',
                     tags='tag1, tag2, tag3')

        Tag.merge('tag', [1, 2, 3])

        self.assertTrue(Tag.query.count() == 1 and
                        p.tags == ['tag'])
