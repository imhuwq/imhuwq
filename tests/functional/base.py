from unittest import TestCase
from selenium import webdriver
from app import create_app, db
from app.models import User, Settings
import threading
import os
from functools import wraps
from selenium.common.exceptions import NoSuchElementException

chrome_driver = os.path.abspath(os.path.dirname(__file__) + '/chromedriver')


class FunctionalTest(TestCase):
    client = None

    def find_or_None(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except NoSuchElementException:
                result = None
            return result

        return wrapper

    @classmethod
    def setUpClass(cls):
        try:
            cls.client = webdriver.Chrome(executable_path=chrome_driver)
        except:
            pass

        if cls.client:
            # 创建 app
            cls.app = create_app('test')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 建立数据库
            db.create_all()
            setting = Settings(
                site_admin_email='test@example.com',
                site_initiated=True,
            )
            db.session.add(setting)
            db.session.commit()

            user = User(
                name='test_user',
                password='catanddog',
                email='test@example.com'
            )
            db.session.add(user)
            db.session.commit()

            cls.host = 'http://localhost:5000'

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 关闭服务器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            # 销毁数据库
            db.drop_all()
            db.session.remove()

            # 移除 app
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')
        self.client.implicitly_wait(1)

    def tearDown(self):
        pass
