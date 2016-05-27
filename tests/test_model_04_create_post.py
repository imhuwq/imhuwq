# -*- coding: utf8 -*-
"""
    test.test_model_04_create_post
    ~~~~~~~~~~~~~~~~~~~~~~~~

    测试基本的分类和标签的创建
"""

import unittest
from app import create_app, db
from app.models import Category, Tag, Post


class BasicTestCase(unittest.TestCase):
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
