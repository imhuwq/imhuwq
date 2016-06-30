import unittest
from flask import current_app
from app import create_app, db


class BasicTestCase(unittest.TestCase):
    """测试基本的测试环境"""
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_app_exists(self):
        """测试app存在"""
        self.assertFalse(current_app is None)

    def test_02_app_is_testing(self):
        """测试app模式为测试模式"""
        self.assertTrue(current_app.config['TESTING'])
