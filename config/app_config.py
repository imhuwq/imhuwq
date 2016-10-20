# encoding: utf-8

import os
import random
import string

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

characters = string.ascii_letters + string.digits


def generate_secret_key(length=60):
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))


class Config:
    #  ---------------------------------------------   #
    #  编辑以下区域以配置您的网站　　　　　　　　　　　　　　 #
    #  ---------------------------------------------  #

    # 数据库名称
    DATABASE_NAME = ''

    # 数据库服务器
    DATABASE_HOST = ''

    # 用于链接数据库的用户名
    #    如果此处为空，则默认使用sqlite数据库
    DATABASE_USERNAME = ''

    # 数据库用户密码
    DATABASE_PASSWORD = ''

    #  ---------------------------------------------  #
    #  编辑　**以上**　区域以配置您的网站　　　　　  #
    #  --------------------------------------------   #

    #  ---------------------------------------------  #
    #  请不要编辑以下区域                　　　　　  #
    #  --------------------------------------------   #

    # 通用设置
    SECRET_KEY = generate_secret_key()

    PREFERRED_URL_SCHEME = 'https'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SITE_INITIATED = False

    def __init__(self, app=None):
        self.DEBUG = None
        self.TESTING = None
        self.SQLALCHEMY_DATABASE_URI = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        mode = app.mode
        # 默认生产模式
        if mode == 'production':
            db_name = 'production.sqlite'

        # 测试模式
        elif mode == 'testing':
            self.TESTING = True
            db_name = 'testing.sqlite'

        # 开发模式
        elif mode == 'develop':
            self.DEBUG = True
            db_name = 'develop.sqlite'
        else:
            raise AttributeError('an app should be run in production, develop or testing mode')

        # 不提供数据库名则使用 sqlite
        if self.DATABASE_NAME == '' or mode == 'test':
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, db_name)

        # 否则使用 postgresql
        else:
            self.SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s/%s' \
                                           % (self.DATABASE_USERNAME, self.DATABASE_PASSWORD,
                                              self.DATABASE_HOST, self.DATABASE_NAME)
        app.config.from_object(self)
