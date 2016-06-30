from .. import db, login_manager
from flask import current_app
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin


class Settings(db.Model):
    """存储基本的站点设置"""
    __tablename__ = 'settings'

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


class User(db.Model, UserMixin):
    """用户Model
       只需要邮箱, 和hash密码
       密码不可读,但是可以用verify_password(passwd)对passwd进行验证
       当创建用户时,如果用户邮箱与app.config中的管理员邮箱一致,则赋予用户管理员属性
    """
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

    def __init__(self, **kwargs):
        """当创建用户时,如果用户邮箱与app.config中的管理员邮箱一致,则赋予用户管理员属性"""
        super().__init__(**kwargs)
        if not self.is_administrator:
            self.is_administrator = self.email == current_app.config['SITE_ADMIN_EMAIL']


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


@event.listens_for(User.email, 'set')
def update_admin_email(target, value, oldvalue, initiator):
    if target.is_administrator:
        sets = Settings.query.get(1)
        sets.site_admin_email = value
        sets.update_site_settings()
