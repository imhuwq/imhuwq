from .. import db
from datetime import datetime
from sqlalchemy import event, or_


class Post(db.Model):
    __tablename__ = 'blog_posts'
    _id = db.Column('id', db.Integer, primary_key=True)

    #: _type和_main_id一起用来区分日志的类型
    #: if _type == 'article' and not _main_id: 已发布的文章
    #: if _type == 'draft' and not _main_id: 未发布的文章
    #: if _type == 'draft' and _main_id: 已发布的文章的修改稿, 已发布的文章的id为_main_id
    _type = db.Column('type', db.String(16))
    _main_id = db.Column('main_id', db.Integer)

    #: _tile即文章的标题, _link是文章的uri, 对于已发布的文章来说, 二者都必须保证唯一性
    _title = db.Column('title', db.String(128))
    _link = db.Column('link', db.String(128), index=True)

    #: _publish_date在文章第一次发表时设置
    #: _edit_date 在文章草稿发布时设置
    #: 后者会在文章详情页显示,以体现文章内容的时效性, 前者用于文章按时间排名
    _publish_date = db.Column('publish_date', db.DateTime)
    _edit_date = db.Column('edit_date', db.DateTime)

    #: _content即日志内容, _abstract为摘要
    _content = db.Column('content', db.Text)
    _abstract = db.Column('abstract', db.Text)

    #: _commendable是日志可评论状态, False不可评论,也不会显示以前的评论
    #: 可评论状态受博客全局可评论设置影响,结果为 settings.enable_post_comment & post.commendable
    _commendable = db.Column('commendable', db.Boolean, default=True)

    #: _public是日志的对外可见状态, False则只有管理员可见
    _public = db.Column('public', db.Boolean, default=True)

    #: _category存储的是文章所属分类的link,包含分类的集成关系信息
    _category = db.Column('category', db.String(128), index=True)

    #: _tags存储的是文章拥有的标签的字符串, 分割符为: ,
    _tags = db.Column('tags', db.String(128), index=True)

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title or ''

    @title.setter
    def title(self, title):
        if len(title) > 120:
            raise AttributeError('标题最多120个字符')

        # 不允许两篇article的标题相同
        p = Post.query.filter_by(_title=title).first()
        if p and p.type == 'article' and self.type == 'article':
            if not self.id or self.id != p.id:
                raise AttributeError('标题重复')

        self._title = title
        self._link = title.replace(' ', '_')

    @property
    def link(self):
        return self._link or ''

    @property
    def date(self):
        return self._edit_date or None

    @property
    def publish_date(self):
        return self._publish_date or None

    @property
    def content(self):
        return self._content or ''

    @content.setter
    def content(self, content):
        self._content = content
        # 根据content生成abstract
        self._abstract = content.split('<!--more-->', 1)[0]

    @property
    def abstract(self):
        return self._abstract or ''

    @property
    def category(self):
        if self._category:
            cate = Category.query.filter_by(_link=self._category).first()
            return cate
        return None

    @category.setter
    def category(self, cate):
        if not cate:
            cate = Category.query.get(1)
            if not cate:
                cate = Category(name='默认分类')
                db.session.add(cate)

        old_link = self._category
        new_link = cate.link
        self._category = cate.link
        db.session.add(self)

        old_names = old_link.split('/') if old_link else []
        if old_names:
            old_ancestors = [old_names.pop(0)]
            for name in old_names:
                old_ancestors.append('/'.join([old_ancestors[-1], name]))
        else:
            old_ancestors = []

        new_names = new_link.split('/') if new_link else []
        if new_names:
            new_ancestors = [new_names.pop(0)]
            for name in new_names:
                new_ancestors.append('/'.join([new_ancestors[-1], name]))
        else:
            new_ancestors = []

        del_ancestors = [x for x in old_ancestors if x not in new_ancestors]
        for link in del_ancestors:
            ancestor = Category.query.filter_by(_link=link).first()
            if ancestor:
                ancestor.refresh_posts_count()

        for link in new_ancestors:
            ancestor = Category.query.filter_by(_link=link).first()
            if ancestor:
                ancestor.refresh_posts_count()

    @property
    def tags(self):
        return self._tags.split(',') if self._tags else []

    @tags.setter
    def tags(self, tags):
        if not tags:
            tags = ''
        old_tags = self._tags.split(',') if self._tags else []
        new_tags = [tag.strip().lower() for tag in tags.split(',') if tag != '']
        del_tags = [x for x in old_tags if x not in new_tags]

        self._tags = ','.join(new_tags)
        db.session.add(self)

        for tag in new_tags:
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
        return Post.query.filter(Post._main_id == self._id).first() or None

    @property
    def main(self):
        if self._main_id:
            return Post.query.get(self._main_id)
        else:
            return None

    @property
    def type(self):
        return self._type

    @property
    def public(self):
        return self._public

    @public.setter
    def public(self, value):
        if value in [1, '1', 'True', 'public', 'open', True]:
            self._public = True
        else:
            self._public = False
        self.category.refresh_posts_count()
        for tag in self.tags:
            t = Tag.query.filter_by(_name=tag).first()
            t.refresh_posts_count()

    @property
    def commendable(self):
        return self._commendable

    @commendable.setter
    def commendable(self, value):
        if value in [1, '1', 'True', 'commendable', 'on', True]:
            self._commendable = True
        else:
            self._commendable = False

    def add_tag(self, tag):
        if self._tags:
            self._tags = self._tags + ',' + tag.name if tag.name not in self.tags else self._tags
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
    def publish(post, **data):
        """ 如果post为修改稿, 先
                找到main post,
                更新main post内容, main_post.date = utcnow(),
                再删除post
        """
        if post.type == 'draft' and post._main_id:
            main = post.main
            db.session.delete(post)
            post = main
        db.session.add(post)
        post._type = 'article'
        post.title = data.get('title', '')
        post.content = data.get('content', '')
        post.category = data.get('category', None)
        post.tags = data.get('tags', None)
        post.commendable = data.get('commendable', True)
        post.public = data.get('public', True)
        post._edit_date = datetime.utcnow().replace(microsecond=0)
        post._publish_date = post._publish_date or post._edit_date
        db.session.commit()

    @staticmethod
    def save(post, **data):
        """ 如果post为已发布, 新建edit_post为修改稿, edit_post内容为当前内容,
                                                  edit_post._main_id = post.id
        """
        if post.type == 'article':
            old_draft = post.draft
            if old_draft:
                db.session.delete(old_draft)
            draft = Post()
            draft._main_id = post.id
            post = draft

        post._type = 'draft'
        post.title = data.get('title')
        post.content = data.get('content')
        post.category = data.get('category')
        post.tags = data.get('tags')
        post.commendable = data.get('commendable')
        post.public = data.get('public')
        post._edit_date = datetime.utcnow().replace(microsecond=0)

        db.session.add(post)
        db.session.commit()

    @staticmethod
    def generate_fake(count=30):
        from random import randint
        import forgery_py

        for i in range(count):
            t1 = Tag.query.all()[randint(1, 20)].name
            t2 = Tag.query.all()[randint(1, 20)].name
            t3 = Tag.query.all()[randint(1, 20)].name
            c = Category.query.all()[randint(1, 10)]
            p = Post()
            Post.publish(post=p,
                         title=forgery_py.lorem_ipsum.sentence()[0:110] + str(randint(1, 100)),
                         content=forgery_py.lorem_ipsum.sentences(randint(5, 20)),
                         tags=','.join([t1, t2, t3]),
                         category=c)


class Category(db.Model):
    __tablename__ = 'blog_categories'
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
                self.link = new_name.replace(' ', '_')
            else:
                parent_link = self._link.split('/')[:-1]
                self.link = '%s/%s' % ('/'.join(parent_link), new_name.replace(' ', '_'))
        else:
            self.link = new_name.replace(' ', '_')

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, new_link):
        old_link = self._link
        if old_link:
            children = self.children.all()
            posts = self.posts.all()
            self._link = new_link
            self._level = len(self._link.split('/')) - 1
            self.update_family_tree(children, posts)
        else:
            self._link = new_link
            self._level = len(self._link.split('/')) - 1

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
        if cate:
            if cate.is_descendant_of(self):
                raise AttributeError('%s is descendant of %s, and it can not be its parent directly'
                                     % (cate.name, self._name))
            else:
                self.link = '%s/%s' % (cate.link, self._name.replace(' ', '_'))
        else:
            self.link = self._name.replace(' ', '_')

    @property
    def children(self):
        return Category.query.filter_by(_level=self._level + 1).filter(Category._link.like(self._link + '/%'))

    def is_descendant_of(self, cate):
        return self._link.startswith(cate.link)

    def update_family_tree(self, children=None, posts=None):
        posts = posts or self.posts.all()
        for post in posts:
            post.category = self
        children = children or self.children.all()
        if children:
            for child in children:
                child.link = self._link + '/' + child.name.replace(' ', '_')

    def refresh_posts_count(self):
        self._posts_count = self.all_posts.filter_by(_public=True).count()

    @property
    def posts(self):
        return Post.query.filter(Post._category == self._link).filter(Post._type == 'article')

    @property
    def all_posts(self):
        posts = Post.query.filter(or_(Post._category.like(self._link),
                                      Post._category.like(self._link + '/%'))).filter(Post._type == 'article')
        return posts

    @property
    def posts_count(self):
        return self._posts_count

    @staticmethod
    def generate_fake(count=20):
        import forgery_py
        from random import randint
        suffix = set([])
        while len(suffix) < count:
            suffix.add(randint(1, 100))
        for i in suffix:
            c = Category(
                name=forgery_py.lorem_ipsum.word() + str(i)
            )
            db.session.add(c)
            db.session.commit()

    @staticmethod
    def delete(cate):
        if cate.id == 1:
            raise AttributeError('无法删除默认分类')
        parent = cate.parent
        if not parent:
            parent = Category.query.get(1)
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
        db.session.commit()

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
            if target_cate.id in moved_id_list:
                return {'warning': '<%s>不能成为自己的子分类' % target_name}
        moved_cate_list = [Category.query.get(cate_id) for cate_id in moved_id_list]
        for c in moved_cate_list:
            c.parent = target_cate
        return {'success': 'done'}


class Tag(db.Model):
    __tablename__ = 'blog_tags'
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
        self._posts_count = self.posts.filter_by(_public=True).count()

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
        suffix = set([])
        while len(suffix) < count:
            suffix.add(randint(1, 100))

        for i in suffix:
            t = Tag(
                name=forgery_py.lorem_ipsum.word() + str(i)
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
