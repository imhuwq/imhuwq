import unittest, time
from app import create_app, db
from app.models import Post, Category, Tag


class BasicTestCase(unittest.TestCase):
    """测试文章的发布和保存,以及对应分类标签和分类的统计情况
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
                        p.date == p._publish_date and
                        p.category == c and
                        p.tags == ['tag', 'gat'] and
                        p.link == 'po_st' and
                        p.abstract == 'post_abstract' and
                        p.draft is None and
                        t.posts_count == 1 and
                        t.posts[0] == p and
                        a.posts_count == 1 and
                        a.posts[0] == p and
                        c.posts_count == 1 and
                        c.all_posts[0] == p and
                        c.posts[0] == p)

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
                        p.date is not None and
                        p._publish_date is None and
                        p.category == c and
                        p.tags == ['tag', 'gat'] and
                        p.link == 'po_st' and
                        p.abstract == 'post_abstract' and
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
                        p.date != p._publish_date and
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
                  title='po st article',
                  content='post_abstract<!--more-->post_content',
                  public=True,
                  commendable=False,
                  tags='tag',
                  category=c)

        self.assertTrue(p.type == 'draft' and
                        p.date != p.publish_date and
                        p.category == c and
                        p.tags == ['tag'] and
                        p.link == 'po_st_article' and
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
