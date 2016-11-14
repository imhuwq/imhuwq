from flask import current_app
from flask_sqlalchemy import event

from app import db


class Settings(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    site_admin_email = db.Column(db.String(64))
    site_initiated = db.Column(db.Boolean, default=False)
    enable_post_comment = db.Column(db.Boolean, default=True)
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


@event.listens_for(Settings, 'after_update')
def auto_update_config(mapper, connection, target):
    target.update_site_settings()
