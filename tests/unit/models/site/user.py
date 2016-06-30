# -*- coding: utf8 -*-
import unittest
from flask import current_app, url_for
from app import create_app, db
from app.models import User


class UserTest(unittest.TestCase):
    """用户模块测试"""

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
        """测试管理员更改邮箱"""
        self.client.get(url_for('main.index'))
        email = current_app.config['SITE_ADMIN_EMAIL']
        user = User(email=email,
                    password='fakepassword')
        db.session.add(user)
        db.session.commit()

        user.email = 'new_admin_email@email.com'

        self.assertTrue(current_app.config['SITE_ADMIN_EMAIL'] == 'new_admin_email@email.com')
