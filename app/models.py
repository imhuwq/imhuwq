from . import db, login_manager
from flask import current_app
from datetime import datetime
from sqlalchemy import event, or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
import re


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_admin_email = db.Column(db.String(64))
    site_initiated = db.Column(db.Boolean, default=False)
    enable_post_comment = db.Column(db.Integer, default=1)
    posts_per_page = db.Column(db.Integer, default=20)
    show_abstract = db.Column(db.Boolean, default=True)
    comments_per_page = db.Column(db.Integer, default=20)
    site_title = db.Column(db.String(64), default="一个崭新的网站")
    site_description = db.Column(db.String(128), default="请到管理面板更改设置")
    disqus_identifier = db.Column(db.String(32))
    google_analytics_code = db.Column(db.String(32))

    def update_site_settings(self):
        current_app.config['SITE_INITIATED'] = self.site_initiated
        current_app.config['SITE_ADMIN_EMAIL'] = self.site_admin_email
        current_app.config['ENABLE_COMMENT'] = self.enable_post_comment
        current_app.config['POSTS_PER_PAGE'] = self.posts_per_page
        current_app.config['COMMENTS_PER_PAGE'] = self.comments_per_page
        current_app.config['SHOW_ABSTRACT'] = self.show_abstract
        current_app.config['SITE_TITLE'] = self.site_title
        current_app.config['SITE_DESCRIPTION'] = self.site_description
        current_app.config['GOOGLE_ANALYTICS_CODE'] = self.google_analytics_code
        current_app.config['DISQUS_IDENTIFIER'] = self.disqus_identifier


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(12), unique=True, index=True)
    is_administrator = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    password_period = db.Column(db.DateTime, default=datetime.utcnow())

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_period = datetime.utcnow()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self):
        super().__init__()
        if self.is_administrator is None:
            if self.email == current_app.config['SITE_ADMIN_EMAIL']:
                self.is_administrator = True
            else:
                self.is_administrator = False


@login_manager.user_loader
def user_loader(u_id):
    user_id = int(u_id)
    return User.query.get(user_id)


class AnonymousUser(AnonymousUserMixin):
    @property
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    _id = db.Column('id', db.Integer, primary_key=True)
    _type = db.Column('type', db.String(16))
    _main_id = db.Column('main_id', db.Integer)
    _title = db.Column('title', db.String(128))
    _link = db.Column('link', db.String(128), index=True)
    _publish_date = db.Column('publish_date', db.DateTime)
    _edit_date = db.Column('edit_date', db.DateTime)
    _content = db.Column('content', db.Text)
    _abstract = db.Column('abstract', db.Text)
    _commendable = db.Column('commendable', db.Boolean, default=True)
    _public = db.Column('public', db.Boolean, default=True)
    _category = db.Column('category', db.String(128), index=True)
    _tags = db.Column('tags', db.String(128), index=True)

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self._link = title.replace(' ', '_')

    @property
    def link(self):
        return self._link

    @property
    def date(self):
        return self._edit_date

    @date.setter
    def date(self, date):
        self._edit_date = date

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content
        self._abstract = content.split('<!--more-->', 1)[0]

    @property
    def abstract(self):
        return self._abstract

    @property
    def category(self):
        name = self._category.split('/')[-1]
        return Category.query.filter_by(_name=name).first()

    @category.setter
    def category(self, cate):
        old_link = self._category
        new_link = cate.link

        self._category = cate.link

        old_ancestors = old_link.split('/') if old_link else ''
        new_ancestors = new_link.split('/')
        add_ancestors = [x for x in new_ancestors if x not in old_ancestors]
        del_ancestors = [x for x in old_ancestors if x not in new_ancestors]
        for name in del_ancestors:
            ancestor = Category.query.filter_by(_name=name).first()
            if ancestor:
                ancestor.refresh_posts_count()

        for name in add_ancestors:
            ancestor = Category.query.filter_by(_name=name).first()
            if ancestor:
                ancestor.refresh_posts_count()

    @property
    def tags(self):
        return self._tags.split(',') if self._tags else []

    @tags.setter
    def tags(self, tags):
        old_tags = self._tags.split(',') if self._tags else []
        new_tags = [tag.strip().lower() for tag in tags.split(',') if tag != '']
        add_tags = [x for x in new_tags if x not in old_tags]
        del_tags = [x for x in old_tags if x not in new_tags]

        if new_tags:
            self._tags = ','.join(new_tags)

        for tag in add_tags:
            t = Tag.query.filter_by(_name=tag).first()
            if t is None:
                t = Tag(name=tag)
                db.session.add(t)
            t.refresh_posts_count()
        for tag in del_tags:
            t = Tag.query.filter_by(_name=tag).first()
            t.refresh_posts_count()

    @property
    def draft(self):
        return Post.query.filter(Post._main_id == self._id).first()

    @draft.setter
    def draft(self, draft):
        if self._type == 'draft' or self._main_id is not None:
            raise AttributeError('draft can not have draft')
        draft._main_id = self._id

    @property
    def main(self):
        if self._main_id:
            return Post.query.get(self._main_id)
        else:
            return None

    @main.setter
    def main(self, main):
        self._main_id = main.id

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        if t not in ['article', 'draft']:
            raise AttributeError('only "article" and "draft" are supported')

        self._type = t

    @property
    def public(self):
        return self._public

    @public.setter
    def public(self, value):
        if value in [1, 'True', 'public', 'open', True]:
            self._public = True
        else:
            self._public = False

    @property
    def commendable(self):
        return self._commendable

    @commendable.setter
    def commendable(self, value):
        if value in [1, 'True', 'commendable', 'on', True]:
            self._commendable = True
        else:
            self._commendable = False

    def add_tag(self, tag):
        if self._tags:
            self._tags = self._tags + ',' + tag.name if tag.name not in self._tags else self._tags
        else:
            self._tags = tag.name
        tag.refresh_posts_count()

    def del_tag(self, delete_tag, refresh_posts_count=True):
        tags = self.tags
        new_tags = [tag for tag in tags if tag != delete_tag.name]
        self._tags = ','.join(new_tags)
        if refresh_posts_count:
            delete_tag.refresh_posts_count()

    @staticmethod
    def generate_fake(count=30):
        from random import randint
        import forgery_py

        for i in range(count):
            t1 = Tag.query.all()[randint(1, 20)].name
            t2 = Tag.query.all()[randint(1, 20)].name
            t3 = Tag.query.all()[randint(1, 20)].name
            c = Category.query.all()[randint(1, 10)]
            p = Post(title=forgery_py.lorem_ipsum.sentence(),
                     content=forgery_py.lorem_ipsum.sentences(randint(5, 20)),
                     date=forgery_py.date.date(True),
                     type='article'
                     )
            db.session.add(p)
            p.tags = ','.join(set([t1, t2, t3]))
            p.category = c
            db.session.commit()


class Category(db.Model):
    __tablename__ = 'categories'
    _id = db.Column('id', db.Integer, primary_key=True)
    _name = db.Column('name', db.String(32), unique=True, index=True)
    _link = db.Column('link', db.String(128), unique=True, index=True)
    _level = db.Column('level', db.Integer, default=0, index=True)
    _order = db.Column('order', db.Integer, default=0, index=True)
    _posts_count = db.Column('posts_count', db.Integer, default=0, index=True)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if '/' in new_name:
            raise AttributeError('"/" is not allowed in category name')
        self._name = new_name
        if self._link:
            if self._level == 0:
                self._link = new_name.replace(' ', '_')
            else:
                parent_link = self._link.split('/')[:-1]
                self._link = '%s/%s' % ('/'.join(parent_link), new_name.replace(' ', '_'))
        else:
            self._link = new_name.replace(' ', '_')

    @property
    def link(self):
        return self._link

    @property
    def level(self):
        return self._level

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, new_order):
        self._order = new_order

    @property
    def parent(self):
        if self._level == 0:
            return None
        parent_link = '/'.join(self._link.split('/')[:-1])
        parent = Category.query.filter_by(_link=parent_link).first()
        return parent

    @parent.setter
    def parent(self, cate):
        old_parent = self.parent

        if cate:
            if cate.is_descendant_of(self):
                raise AttributeError('%s is descendant of %s, and it can not be its parent directly'
                                     % (cate.name, self._name))
            else:
                self._link = '%s/%s' % (cate.link, self._name.replace(' ', '_'))
                self._level = len(self._link.split('/')) - 1
                cate.refresh_posts_count()

        else:
            self._link = self._name.replace(' ', '_')
            self._level = 0

        self.update_family_tree()

        if old_parent:
            old_parent.refresh_posts_count()

    @property
    def children(self):
        return Category.query.filter_by(_level=self._level + 1).filter(Category._link.like(self._link + '/%'))

    def is_descendant_of(self, cate):
        return self._link.startswith(cate.link)

    def update_family_tree(self):
        for post in self.posts:
            post.category_link = self._link
        if self.children.all():
            for child in self.children.all():
                child._link = self._link + child.name.replace(' ', '_')
                child.update_family_tree()

    def refresh_posts_count(self):
        count = self.all_posts.count()
        self._posts_count = count

    @property
    def posts(self):
        return Post.query.filter(Post._category == self._link).filter(Post._type == 'article')

    @property
    def all_posts(self):
        return Post.query.filter(or_(Post._category.like(self._link),
                                     Post._category.like(self._link + '/%'))).filter(Post._type == 'article')

    @property
    def posts_count(self):
        return self._posts_count

    @staticmethod
    def generate_fake(count=20):
        import forgery_py
        from random import randint
        for i in range(count):
            c = Category(
                name=forgery_py.lorem_ipsum.word() + str(randint(1, 50))
            )
            db.session.add(c)
            db.session.commit()

    @staticmethod
    def delete(cate):
        parent = cate.parent
        posts = cate.posts
        for post in posts:
            post.category = parent
        for child in cate.children.all():
            child.parent = parent
        db.session.delete(cate)

    @staticmethod
    def marge(new_name, merged_id_list):
        merged_id_list = [int(id) for id in merged_id_list]
        if 1 in merged_id_list:
            new_cate = Category.query.get(1)
            new_cate.name = new_name
        else:
            new_cate = Category.query.filter_by(_name=new_name).first()
            if new_cate is None:
                new_cate = Category(name=new_name)
                db.session.add(new_cate)
                db.session.flush()
        new_id = new_cate._id
        merged_id_list = [x for x in merged_id_list if x != new_id]
        merged_cate_list = [Category.query.get(cate_id) for cate_id in merged_id_list]
        for c in merged_cate_list:
            for p in c.posts:
                p.category = new_cate
            for child in c.children.all():
                child.parent = new_cate
            db.session.delete(c)

    @staticmethod
    def move(target_name, moved_id_list):
        moved_id_list = [int(id) for id in moved_id_list]
        if 1 in moved_id_list:
            name = Category.query.get(1).name
            return {'warning': '<%s>是默认分类, 不能成为任何分类的子分类' % name}
        else:
            target_cate = Category.query.filter_by(_name=target_name).first()
            if target_cate is None:
                target_cate = Category(name=target_name)
                db.session.add(target_cate)
                db.session.flush()
            if target_cate._id in moved_id_list:
                return {'warning': '<%s>不能成为自己的子分类' % target_name}
        moved_cate_list = [Category.query.get(cate_id) for cate_id in moved_id_list]
        for c in moved_cate_list:
            c.parent = target_cate
        return {'success': 'done'}


class Tag(db.Model):
    __tablename__ = 'tags'
    _id = db.Column('id', db.Integer, primary_key=True)
    _name = db.Column('name', db.String(32), unique=True, index=True)
    _link = db.Column('link', db.String(32), unique=True, index=True)
    _posts_count = db.Column('posts_count', db.Integer, default=0)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._link = new_name.replace(' ', '_')

    @property
    def link(self):
        return self._link

    @property
    def posts_count(self):
        return self._posts_count

    def refresh_posts_count(self):
        self._posts_count = self.posts.count()

    @property
    def posts(self):
        query = Post.query.filter(or_(Post._tags.like(self._name),
                                      Post._tags.like(self._name + ',%'),
                                      Post._tags.like('%,' + self._name),
                                      Post._tags.like('%,' + self._name + ',%'))). \
            filter(Post._type == 'article')
        return query

    @staticmethod
    def delete(tag):
        posts = tag.posts.all()
        for post in posts:
            post.del_tag(tag, refresh_posts_count=False)
        db.session.delete(tag)

    @staticmethod
    def merge(new_name, merged_id_list):
        new_tag = Tag.query.filter_by(_name=new_name).first()
        merged_id_list = [int(id) for id in merged_id_list]
        if new_tag is None:
            new_tag = Tag(name=new_name)
            db.session.add(new_tag)
            db.session.flush()
        merged_id_list = [x for x in merged_id_list if x != new_tag.id]
        merged_tag_list = [Tag.query.get(id) for id in merged_id_list]
        for t in merged_tag_list:
            posts = t.posts
            for p in posts:
                p.add_tag(new_tag)
                p.del_tag(t, refresh_posts_count=False)
            Tag.delete(t)

    @staticmethod
    def generate_fake(count=30):
        import forgery_py
        from random import randint

        for i in range(count):
            t = Tag(
                name=forgery_py.lorem_ipsum.word() + str(randint(1, 50))
            )
            db.session.add(t)
            db.session.commit()


# recount tag and category posts count after deleting the post
@event.listens_for(Post, 'after_delete')
def update_category_posts_count(mapper, connection, target):
    if target.type == 'article':
        cate_table = Category.__table__
        category = target.category.link
        ancestors = category.split('/') if category else []
        for name in ancestors:
            ancestor = Category.query.filter_by(_name=name).first()
            if ancestor:
                count = ancestor.all_posts.count()
                connection.execute(
                    cate_table.update().where(cate_table.c.id == ancestor.id).values(posts_count=count)
                )
        tag_table = Tag.__table__
        tags = target.tags
        for name in tags:
            tag = Tag.query.filter_by(_name=name).first()
            if tag:
                count = tag.posts.count()
                connection.execute(
                    tag_table.update().where(tag_table.c.id == tag.id).values(posts_count=count)
                )


@event.listens_for(Settings, 'after_update')
def auto_reload_config(mapper, connection, target):
    target.update_site_settings()


@event.listens_for(User.email, 'set')
def update_admin_email(target, value, oldvalue, initiator):
    if target.is_administrator:
        sets = Settings.query.get(1)
        sets.site_admin_email = value
        sets.update_site_settings()
