# -*- coding: utf8 -*-
"""
    test.test_model_01_site_setting
    ~~~~~~~~~~~~~~~

    测试站点设置,主要是站点设置自动更新
"""

import unittest
from flask import current_app, url_for
from app import create_app, db
from app.models import Settings, User


class BasicTestCase(unittest.TestCase):
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

    def test_01_site_not_initiated(self):
        """测试app没有初始化"""
        resp = self.client.get(url_for('main.index'))
        sets = Settings.query.get(1)
        self.assertTrue(sets is not None and
                        not current_app.config['SITE_INITIATED'] and
                        not sets.site_initiated and
                        '/setup' in resp.get_data(as_text=True))

    def test_02_site_admin(self):
        """测试站点设置自动更新"""
        resp = self.client.get(url_for('main.index'))
        sets = Settings.query.get(1)
        sets.site_initiated = True
        sets.site_admin_email = 'admin@example.com'
        sets.enable_post_comment = 'False'
        sets.posts_per_page = 5
        sets.comments_per_page = 10
        sets.show_abstract = True
        sets.site_title = 'Welcome to ImHuWQ'
        sets.site_description = 'a blog based on Flask'
        sets.google_analytics_code = None
        sets.disqus_identifier = 'welcome'
        db.session.commit()
        self.assertTrue(current_app.config['SITE_INITIATED'] == sets.site_initiated and
                        current_app.config['SITE_ADMIN_EMAIL'] == sets.site_admin_email and
                        current_app.config['ENABLE_COMMENT'] == sets.enable_post_comment and
                        current_app.config['POSTS_PER_PAGE'] == sets.posts_per_page and
                        current_app.config['COMMENTS_PER_PAGE'] == sets.comments_per_page and
                        current_app.config['SHOW_ABSTRACT'] == sets.show_abstract and
                        current_app.config['SITE_TITLE'] == sets.site_title and
                        current_app.config['SITE_DESCRIPTION'] == sets.site_description and
                        current_app.config['GOOGLE_ANALYTICS_CODE'] == sets.google_analytics_code and
                        current_app.config['DISQUS_IDENTIFIER'] == sets.disqus_identifier)
