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
    comments_per_page = db.Column(db.Integer, default=20)
    site_title = db.Column(db.String(64), default="一个崭新的网站")
    site_description = db.Column(db.String(128), default="请到管理面板更改设置")

    def update_site_settings(self):
        current_app.config['SITE_INITIATED'] = self.site_initiated
        current_app.config['SITE_ADMIN_EMAIL'] = self.site_admin_email
        current_app.config['ENABLE_COMMENT'] = self.enable_post_comment
        current_app.config['POSTS_PER_PAGE'] = self.posts_per_page
        current_app.config['COMMENTS_PER_PAGE'] = self.comments_per_page
        current_app.config['SITE_TITLE'] = self.site_title
        current_app.config['SITE_DESCRIPTION'] = self.site_description


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
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(8))
    main_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    draft = db.relationship('Post', uselist=False, backref=db.backref('main', remote_side=[id]))
    title = db.Column(db.String(32))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    body = db.Column(db.Text)
    abstract = db.Column(db.Text)
    commendable = db.Column(db.Boolean, default=True)
    publicity = db.Column(db.Boolean, default=True)
    tags_name = db.Column(db.String(128))
    category_name = db.Column(db.String(8), index=True)
    category_link = db.Column(db.String(128), index=True)

    @property
    def category(self):
        return self.category_name

    @category.setter
    def category(self, cate):
        old_link = self.category_link
        old_name = self.category_name

        new_link = cate.link

        self.category_name = cate.name
        self.category_link = cate.link

        if self.type == 'article':
            old_ancestors = old_link.split('/') if old_link else ''
            new_ancestors = new_link.split('/')
            if old_ancestors == new_ancestors:
                for name in old_ancestors:
                    ancestor = Category.query.filter_by(_name=name).first()
                    if ancestor:
                        ancestor.refresh_posts_count()
            else:
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
        return self.tags_name

    @tags.setter
    def tags(self, tags):
        old_tags = self.tags_name.split(',') if self.tags_name else []
        new_tags = [tag for tag in tags.split(',') if tag != '']
        for tag in new_tags:
            if Tag.query.filter_by(name=tag).first() is None:
                t = Tag(name=tag)
                db.session.add(t)
        self.tags_name = ','.join(new_tags)
        db.session.flush()

        if self.type == 'article':
            if old_tags == new_tags:
                for tag in old_tags:
                    t = Tag.query.filter_by(name=tag).first()
                    t.refresh_posts_count()
            else:
                add_tags = [x for x in new_tags if x not in old_tags]
                del_tags = [x for x in old_tags if x not in new_tags]
                for tag in del_tags:
                    t = Tag.query.filter_by(name=tag).first()
                    t.refresh_posts_count()
                for tag in add_tags:
                    t = Tag.query.filter_by(name=tag).first()
                    t.refresh_posts_count()

    def add_tag(self, tag):
        self.tags_name = self.tags_name + '、' + tag.name if self.tags_name else tag.name
        tag.refresh_posts_count()

    def del_tag(self, delete_tag, refresh_posts_count=True):
        tags = self.tags_name.split('、') if self.tags_name else []
        new_tags = [tag for tag in tags if tag != delete_tag.name]
        self.tags_name = '、'.join(new_tags)
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
                     body=forgery_py.lorem_ipsum.sentences(randint(5, 20)),
                     date=forgery_py.date.date(True),
                     type='article'
                     )
            db.session.add(p)
            p.tags = '、'.join(set([t1, t2, t3]))
            p.category = c
            db.session.commit()


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column('name', db.String(32), unique=True, index=True)
    _link = db.Column('link', db.String(190), unique=True, index=True)
    level = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    order = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)

    def be_child_of(self, cate):
        if cate:
            if cate.is_descendant_of(self):
                raise AttributeError('%s is descendant of %s, and it can not be its parent directly'
                                     % (cate.name, self.name))
            else:
                self.parent_id = cate.id
                self.link = '%s/%s' % (cate.link, self.name)
                self.level = len(self.link.split('/')) - 1
                db.session.add(self)
                db.session.commit()
        else:
            self.parent_id = None
            self.link = self.name
            self.level = 0
            db.session.add(self)
            db.session.commit()

    def is_descendant_of(self, cate):
        return self.link.startswith(cate.link)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if '/' in new_name:
            raise ValueError('“/” is not allowed in Category Name \n 分类名中不能包含“/”')
        self._name = new_name
        if not self.link or len(self.link.split('/')) == 1:
            self.link = new_name
        else:
            ancestors = self.link.split('/')
            self.link = '/'.join(ancestors[:-1]) + '/' + new_name

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, new_link):
        old_link = self._link
        self._link = new_link

        if old_link:
            posts = Post.query.filter_by(category_link=old_link).all()
            for post in posts:
                post.category = self
            children = self.children
            for child in children:
                child.link = new_link + '/' + child.name

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

    def delete_category(self):
        parent = self.parent
        if not parent:
            parent = Category.query.get(1)
        posts = Post.query.filter_by(category_link=self.link).all()
        for post in posts:
            post.category = parent
        children = self.children
        for child in children:
            child.be_child_of(parent)
        db.session.delete(self)

    def refresh_posts_count(self):
        count = Post.query.filter(or_(Post.category_link.like(self.link),
                                      Post.category_link.like(self.link + '/%'))).count()
        self.posts_count = count

    @staticmethod
    def marge(new_name, merged_id_list):
        if '1' in merged_id_list:
            new_cate = Category.query.get(1)
            new_cate.name = new_name
        else:
            new_cate = Category.query.filter_by(_name=new_name).first()
            if new_cate is None:
                new_cate = Category(name=new_name)
                db.session.add(new_cate)
                db.session.flush()
        new_id = str(new_cate.id)
        merged_id_list = [x for x in merged_id_list if x != new_id]
        merged_cate_list = [Category.query.get(cate_id) for cate_id in merged_id_list]
        for c in merged_cate_list:
            posts = Post.query.filter_by(category_link=c.link).all()
            for p in posts:
                p.category = new_cate
            for child in c.children:
                child.be_child_of(new_cate)
            db.session.delete(c)

    @staticmethod
    def move(target_name, moved_id_list):
        if '1' in moved_id_list:
            name = Category.query.get(1).name
            return {'warning': '<%s>是默认分类, 不能成为任何分类的子分类' % name}
        else:
            target_cate = Category.query.filter_by(_name=target_name).first()
            if target_cate is None:
                target_cate = Category(name=target_name)
                db.session.add(target_cate)
                db.session.flush()
            if str(target_cate.id) in moved_id_list:
                return {'warning': '<%s>不能成为自己的子分类' % target_name}
        moved_cate_list = [Category.query.get(cate_id) for cate_id in moved_id_list]
        for c in moved_cate_list:
            c.be_child_of(target_cate)
        return {'success': 'done'}


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    posts_count = db.Column(db.Integer, default=0)

    @property
    def posts(self):
        query = Post.query.filter(or_(Post.tags_name.like(self.name),
                                      Post.tags_name.like(self.name + ',%'),
                                      Post.tags_name.like('%,' + self.name),
                                      Post.tags_name.like('%,' + self.name + ',%')))
        return query

    def refresh_posts_count(self):
        self.posts_count = self.posts.count()

    def delete_tag(self):
        posts = self.posts.all()
        for post in posts:
            post.del_tag(self, refresh_posts_count=False)
        db.session.delete(self)

    @staticmethod
    def merge(new_name, merged_id_list):
        new_tag = Tag.query.filter_by(name=new_name).first()
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
            t.delete_tag()

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


@event.listens_for(Post.body, 'set')
def generate_abstract(target, value, oldvalue, initiator):
    target.abstract = re.split(r'\r?\n?\r?\n?<!\s*--more--\s*>', value, 1)[0]


@event.listens_for(Post, 'after_delete')
def update_category_posts_count(mapper, connection, target):
    if target.type == 'article':
        cate_table = Category.__table__
        category = target.category_link
        ancestors = category.split('/')
        for name in set(ancestors):
            ancestor = Category.query.filter_by(_name=name).first()
            if ancestor:
                count = ancestor.posts_count - 1
                connection.execute(
                    cate_table.update().where(cate_table.c.id == ancestor.id).values(posts_count=count)
                )
        tag_table = Tag.__table__
        tags = target.tags_name.split('、')
        for name in tags:
            tag = Tag.query.filter_by(name=name).first()
            if tag:
                count = tag.posts_count - 1
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


@event.listens_for(User.password_hash, 'set')
def update_password_period(target, value, oldvalue, initiator):
    target.password_period = datetime.utcnow()
