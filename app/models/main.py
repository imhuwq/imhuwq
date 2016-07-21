from .. import db, login_manager
from config import BASE_DIR
import json
from flask import current_app
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

TRUE = [1, '1', 'true', 'True', True, 'On', 'on']


class Settings(db.Model):
    """存储基本的站点设置"""
    __tablename__ = 'site_settings'
    _id = db.Column("id", db.Integer, primary_key=True)
    _site_admin_email = db.Column("site_admin_email", db.String(64))
    _site_initiated = db.Column("site_initiated", db.Boolean, default=False)
    _enable_post_comment = db.Column("enable_post_comment", db.Boolean, default=True)
    _posts_per_page = db.Column("posts_per_page", db.Integer, default=20)
    _show_abstract = db.Column("show_abstract", db.Boolean, default=True)
    _comments_per_page = db.Column("comments_per_page", db.Integer, default=20)
    _site_title = db.Column("site_title", db.String(64), default="一个崭新的网站")
    _site_description = db.Column("site_description", db.String(128), default="请到管理面板更改设置")
    _disqus_identifier = db.Column("disqus_identifier", db.String(32))
    _google_analytics_code = db.Column("google_analytics_code", db.String(32))

    @property
    def id(self):
        return self._id

    @property
    def site_admin_email(self):
        return self._site_admin_email

    @site_admin_email.setter
    def site_admin_email(self, v):
        self._site_admin_email = v

    @property
    def site_initiated(self):
        return self._site_initiated

    @site_initiated.setter
    def site_initiated(self, v):
        if v in TRUE:
            self._site_initiated = True
        else:
            self._site_initiated = False

    @property
    def enable_post_comment(self):
        return self._enable_post_comment

    @enable_post_comment.setter
    def enable_post_comment(self, v):
        if v in TRUE:
            self._enable_post_comment = True
        else:
            self._enable_post_comment = False

    @property
    def posts_per_page(self):
        return self._posts_per_page

    @posts_per_page.setter
    def posts_per_page(self, v):
        self._posts_per_page = v

    @property
    def show_abstract(self):
        return self._show_abstract

    @show_abstract.setter
    def show_abstract(self, v):
        if v in TRUE:
            self._show_abstract = True
        else:
            self._show_abstract = False

    @property
    def comments_per_page(self):
        return self._comments_per_page

    @comments_per_page.setter
    def comments_per_page(self, v):
        self._comments_per_page = v

    @property
    def site_title(self):
        return self._site_title

    @site_title.setter
    def site_title(self, v):
        self._site_title = v

    @property
    def site_description(self):
        return self._site_description

    @site_description.setter
    def site_description(self, v):
        self._site_description = v

    @property
    def disqus_identifier(self):
        return self._disqus_identifier

    @disqus_identifier.setter
    def disqus_identifier(self, v):
        self._disqus_identifier = v

    @property
    def google_analytics_code(self):
        return self._google_analytics_code

    @google_analytics_code.setter
    def google_analytics_code(self, v):
        self._google_analytics_code = v

    def update_site_settings(self):
        """每次更新设置后,都会触发该函数,对app.config进行更新.
           触发点是sqlalchemy的event.listens_for
        """
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

    @staticmethod
    def export_json(target_url=None, export_directly=True):
        if not target_url:
            target_url = BASE_DIR
        columns = Settings.__table__.columns
        sets = Settings.query.all()
        sets_data = [{
                         column.key: getattr(set, '_' + column.key) for column in columns
                         }
                     for set in sets]
        if export_directly:
            with open('%s/settings.json' % target_url, 'w') as j:
                json.dump(sets_data, j)
        return sets_data


class User(db.Model, UserMixin):
    """用户Model
       只需要邮箱, 和hash密码
       密码不可读,但是可以用verify_password(passwd)对passwd进行验证
       当创建用户时,如果用户邮箱与app.config中的管理员邮箱一致,则赋予用户管理员属性
    """
    __tablename__ = 'site_users'
    _id = db.Column("id", db.Integer, primary_key=True)
    _email = db.Column("email", db.String(64), unique=True, index=True)
    _name = db.Column("name", db.String(12), unique=True, index=True)
    _is_administrator = db.Column("is_administrator", db.Boolean)
    _password_hash = db.Column("password_hash", db.String(128))

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, v):
        self._email = v

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        self._name = v

    @property
    def is_administrator(self):
        return self._is_administrator

    @is_administrator.setter
    def is_administrator(self, v):
        self._is_administrator = v

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __init__(self, **kwargs):
        """当创建用户时,如果用户邮箱与app.config中的管理员邮箱一致,则赋予用户管理员属性"""
        super().__init__(**kwargs)
        if not self._is_administrator:
            self._is_administrator = self.email == current_app.config['SITE_ADMIN_EMAIL']

    @staticmethod
    def export_json(target_dir=None, export_directly=True):
        if not target_dir:
            target_dir = BASE_DIR
        columns = User.__table__.columns
        users = Settings.query.all()
        users_data = [{
                          column.key: getattr(user, '_' + column.key) for column in columns
                          }
                      for user in users]
        if export_directly:
            with open('%s/users.json' % target_dir, 'w') as j:
                json.dump(users_data, j)
        return users_data


@login_manager.user_loader
def user_loader(u_id):
    user_id = int(u_id)
    return User.query.get(user_id)


class AnonymousUser(AnonymousUserMixin):
    @property
    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@event.listens_for(Settings, 'after_update')
def auto_reload_config(mapper, connection, target):
    target.update_site_settings()


@event.listens_for(User._email, 'set')
def update_admin_email(target, value, oldvalue, initiator):
    if target.is_administrator:
        sets = Settings.query.get(1)
        sets.site_admin_email = value
        sets.update_site_settings()
