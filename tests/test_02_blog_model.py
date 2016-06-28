import unittest
from flask import current_app, url_for
from app import create_app, db
# -*- coding: utf8 -*-
from app.models import User, Post, Tag, Category
import time


class UserTest(unittest.TestCase):
    """测试基本的测试环境"""

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_user_is_not_admin(self):
        """测试用户不为admin"""
        user = User(email='fake_admin@example.com',
                    password='fakepassword')
        db.session.add(user)
        db.session.commit()

        self.assertTrue(not user.is_administrator)

    def test_02_user_is_admin(self):
        """测试用户为admin"""
        email = current_app.config['SITE_ADMIN_EMAIL']
        user = User(email=email,
                    password='fakepassword')
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.is_administrator)

    def test_03_user_password_is_unreadable(self):
        """测试用户密码不可读"""
        email = current_app.config['SITE_ADMIN_EMAIL']
        user = User(email=email,
                    password='fakepassword')
        db.session.add(user)
        db.session.commit()

        self.assertRaises(AttributeError, lambda: user.password)

    def test_04_admin_reset_email(self):
        self.client.get(url_for('main.index'))
        email = current_app.config['SITE_ADMIN_EMAIL']
        user = User(email=email,
                    password='fakepassword')
        db.session.add(user)
        db.session.commit()

        user.email = 'new_admin_email@email.com'

        self.assertTrue(current_app.config['SITE_ADMIN_EMAIL'] == 'new_admin_email@email.com')


class CreateCategoryTest(unittest.TestCase):
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


class CreatePostTest(unittest.TestCase):
    """测试基本的创建文章"""

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

        tag1 = Tag(name='tag1')
        tag2 = Tag(name='tag2')
        tag3 = Tag(name='tag3')
        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_create_post(self):
        """测试发表文章成功"""
        p = Post()
        Post.publish(post=p,
                     title='post',
                     content='post',
                     )
        p = Post.query.filter_by(_title='post').first()
        self.assertTrue(p is not None and
                        p.content == 'post' and
                        p.title == 'post' and
                        p.abstract == 'post' and
                        p.tags == [] and
                        p.category == Category.query.get(1))

    def test_02_post_title(self):
        """测试文章标题不能重复"""
        p = Post()
        Post.publish(post=p,
                     title='post',
                     content='post'
                     )

        p2 = Post()
        self.assertRaises(AttributeError, lambda: Post.publish(post=p2, title='post'))

    def test_03_post_link(self):
        """测试文章link替代文章标题空格为下划线"""
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post'
                     )
        self.assertTrue(p.link == 'po_st')

    def test_04_post_abstract(self):
        """测试文章摘要"""

        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content'
                     )
        self.assertTrue(p.abstract == 'post_abstract')

    def test_05_post_tag(self):
        """测试文章设置和修改标签"""
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     tags='tag1, tag2, tag3'
                     )

        tag1 = Tag.query.filter_by(_name='tag1').first()
        tag2 = Tag.query.filter_by(_name='tag2').first()
        tag3 = Tag.query.filter_by(_name='tag3').first()

        Post.publish(post=p,
                     tags='tag2, tag3, tag4'
                     )
        tag4 = Tag.query.filter_by(_name='tag4').first()

        self.assertTrue(tag1.posts_count == 0 and
                        tag2.posts_count == 1 and
                        tag3.posts_count == 1 and
                        tag4.posts_count == 1 and
                        p.tags == ['tag2', 'tag3', 'tag4'])

    def test_06_post_add_del_tag(self):
        """测试文章增加和删除标签"""
        p = Post()
        tag1 = Tag.query.filter_by(_name='tag1').first()
        tag2 = Tag.query.filter_by(_name='tag2').first()
        tag3 = Tag.query.filter_by(_name='tag3').first()

        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     tags='tag1, tag2'
                     )

        p.add_tag(tag3)
        p.del_tag(tag1)

        self.assertTrue(tag1.posts_count == 0 and
                        tag2.posts_count == 1 and
                        tag3.posts_count == 1 and
                        p.tags == ['tag2', 'tag3'])

    def test_07_post_category(self):
        """测试文章设置和修改分类"""
        cate1 = Category.query.filter_by(_name='cate1').first()
        cate2 = Category.query.filter_by(_name='cate2').first()
        cate3 = Category.query.filter_by(_name='cate3').first()

        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     category=cate3
                     )

        Post.publish(post=p,
                     category=cate2)

        self.assertTrue(cate1.posts_count == 1 and
                        cate2.posts_count == 1 and
                        cate3.posts_count == 0 and
                        p.category == cate2)

    def test_08_post_public(self):
        """测试文章公开程度, 默认公开, 可设置为公开和私密"""
        p = Post()
        Post.publish(post=p,
                     title='post1')

        p2 = Post()
        Post.publish(post=p2,
                     title='post2',
                     public=False)

        Post.publish(post=p2,
                     public=True)

        self.assertTrue(p.public and
                        p2.public)

    def test_09_post_commendable(self):
        """测试文章可评论程度, 默认可评论, 可设置为可评论和不可评论"""
        p = Post()
        Post.publish(post=p,
                     title='post1')

        p2 = Post()
        Post.publish(post=p2,
                     title='post2',
                     commendable=False)

        Post.publish(post=p2,
                     commendable=True)

        self.assertTrue(p.commendable and
                        p2.commendable)

    def test_10_generate_post(self):
        """测试批量增加文章"""
        Tag.generate_fake(40)
        Category.generate_fake(30)
        Post.generate_fake()
        self.assertTrue(Post.query.count() == 30)


class PubAndSavePostTest(unittest.TestCase):
    """测试发布文章和保存文章时文章的状态,以及应分类标签和分类的统计情况
       情况大致如下:
       test_publish_new_post                    新建一篇文章, 直接发布
       test_save_new_post                       新建一篇文章, 不发布而保存为草稿
       test_edit_publish_post                   修改一篇文章, 直接发布
       test_edit_save_post                      修改一篇文章, 不发布, 保存为修改稿
       test_edit_publish_draft                  修改一篇草稿, 直接发布
       test_edit_save_draft                     修改一篇草稿, 继续保存为草稿
       test_edit_publish_edit                   修改一篇修改稿, 直接发布
       test_edit_save_edit                      修改一篇修改稿, 继续保存为修改稿
    """

    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        cate = Category(name='cate')
        tag = Tag(name='tag')
        gat = Tag(name='gat')
        db.session.add_all([cate, tag, gat])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_publish_new_post(self):
        """新建一篇文章,直接发布"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     public=False,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        p = Post.query.filter_by(_title='po st').first()

        self.assertTrue(p.type == 'article' and
                        p.date == p.publish_date and
                        p.draft is None and
                        p.main is None)

    def test_02_save_new_post(self):
        """新建一篇文章, 不发布而保存为草稿"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.save(post=p,
                  title='po st',
                  content='post_abstract<!--more-->post_content',
                  public=False,
                  commendable=False,
                  tags='tag, gat',
                  category=c)

        p = Post.query.filter_by(_title='po st').first()

        self.assertTrue(p.type == 'draft' and
                        p.date and
                        not p.publish_date and
                        p.category == c and
                        p.tags == ['tag', 'gat'] and
                        p.draft is None and
                        t.posts_count == 0 and
                        a.posts_count == 0 and
                        c.posts_count == 0)

    def test_03_edit_publish_post(self):
        """修改一篇文章, 直接发布"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     public=False,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        p = Post.query.filter_by(_title='po st').first()
        time.sleep(1)
        Post.publish(post=p,
                     title='po st 2nd',
                     content='post_abstract<!--more-->post_content',
                     public=True,
                     commendable=True,
                     tags=None,
                     category=c)

        self.assertTrue(p.type == 'article' and
                        p.date != p.publish_date and
                        p.category == c and
                        p.tags == [] and
                        p.link == 'po_st_2nd' and
                        p.public and
                        p.commendable and
                        p.abstract == 'post_abstract' and
                        p.draft is None and
                        t.posts_count == 0 and
                        a.posts_count == 0 and
                        c.posts_count == 1 and
                        c.all_posts[0] == p and
                        c.posts[0] == p)

    def test_04_edit_save_post(self):
        """修改一篇文章, 不发布, 保存为修改稿"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     public=False,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        p = Post.query.filter_by(_title='po st').first()

        Post.save(post=p,
                  title='po st dr af t',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=False,
                  tags='tag',
                  category=None)

        d = p.draft
        self.assertTrue(d is not None and
                        Post.query.count() == 2 and
                        p.type == 'article' and
                        d.type == 'draft' and
                        d.main == p and
                        d.link == 'po_st_dr_af_t' and
                        d.category == c and
                        t.posts_count == 1 and
                        a.posts_count == 1 and
                        d.tags == ['tag'] and
                        c.posts_count == 1)

    def test_05_edit_publish_draft(self):
        """修改一篇草稿, 直接发布"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.save(post=p,
                  title='po st',
                  content='post_abstract<!--more-->post_content',
                  public=False,
                  commendable=False,
                  tags='tag, gat',
                  category=c)

        p = Post.query.filter_by(_title='po st').first()
        Post.publish(post=p,
                     title='po st article',
                     content='post_abstract<!--more-->post_content',
                     public=True,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        self.assertTrue(p.type == 'article' and
                        p.date == p.publish_date and
                        p.category == c and
                        p.tags == ['tag', 'gat'] and
                        p.link == 'po_st_article' and
                        p.public and
                        not p.commendable and
                        p.abstract == 'post_abstract' and
                        p.draft is None and
                        t.posts_count == 1 and
                        a.posts_count == 1 and
                        c.posts_count == 1 and
                        c.all_posts[0] == p and
                        c.posts[0] == p)

    def test_06_edit_save_draft(self):
        """修改一篇草稿, 继续保存为草稿"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.save(post=p,
                  title='po st',
                  content='post_abstract<!--more-->post_content',
                  public=False,
                  commendable=False,
                  tags='tag, gat',
                  category=c)

        p = Post.query.filter_by(_title='po st').first()
        Post.save(post=p,
                  title='po st',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=False,
                  tags='tag',
                  category=c)

        self.assertTrue(p.type == 'draft' and
                        p.date != p.publish_date and
                        p.category == c and
                        p.tags == ['tag'] and
                        p.link == 'po_st' and
                        p.public and
                        not p.commendable and
                        p.abstract == 'post_abstract' and
                        p.draft is None and
                        t.posts_count == 0 and
                        a.posts_count == 0 and
                        c.posts_count == 0)

    def test_07_edit_publish_edit(self):
        """修改一篇修改稿, 直接发布"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     public=False,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        p = Post.query.filter_by(_title='po st').first()

        Post.save(post=p,
                  title='po st dr af t',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=False,
                  tags='tag',
                  category=None)

        d = p.draft

        Post.publish(post=d,
                     title='po st ed it',
                     content='post_abstract<!--more-->post_content',
                     public=True,
                     commendable=True,
                     tags='tag',
                     category=None
                     )

        p = Post.query.filter_by(_title='po st ed it').first()

        self.assertTrue(Post.query.count() == 1 and
                        p.type == 'article' and
                        not p.draft and
                        p.link == 'po_st_ed_it' and
                        p.public and
                        p.commendable and
                        p.category == c and
                        t.posts_count == 1 and
                        a.posts_count == 0 and
                        p.tags == ['tag'] and
                        c.posts_count == 1)

    def test_08_edit_save_edit(self):
        """修改一篇修改稿, 继续保存为修改稿"""

        t = Tag.query.filter_by(_name='tag').first()
        a = Tag.query.filter_by(_name='gat').first()
        c = Category.query.filter_by(_name='cate').first()
        p = Post()
        Post.publish(post=p,
                     title='po st',
                     content='post_abstract<!--more-->post_content',
                     public=False,
                     commendable=False,
                     tags='tag, gat',
                     category=c)

        p = Post.query.filter_by(_title='po st').first()

        Post.save(post=p,
                  title='po st dr af t',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=False,
                  tags='tag',
                  category=None)

        d = p.draft

        Post.save(post=d,
                  title='po st ed it',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=True,
                  tags='tag',
                  category=None
                  )

        p = Post.query.filter_by(_title='po st').first()
        d = p.draft

        self.assertTrue(Post.query.count() == 2 and
                        p.type == 'article' and
                        p.draft and
                        p.link == 'po_st' and
                        not p.public and
                        not p.commendable and
                        p.category == c and
                        t.posts_count == 1 and
                        a.posts_count == 1 and
                        t.posts[0] == p and
                        a.posts[0] == p and
                        p.tags == ['tag', 'gat'] and
                        c.posts_count == 1 and
                        c.posts[0] == p and
                        d.main == p and
                        d.title == 'po st ed it' and
                        d.public and d.commendable and
                        d.tags == ['tag'] and
                        d.category == c and
                        d.type == 'draft')


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
