# -*- coding: utf-8 -*-
"""
    General configurations of this app
"""

import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    #  ---------------------------------------------   #
    #  编辑以下区域以配置您的网站　　　　　　　　　　　　　　 #
    #  ---------------------------------------------  #

    # 使用该邮箱注册的用户将成为本站管理员
    SITE_ADMIN_EMAIL = ''

    # 数据库名称
    DATABASE_NAME = ''

    # 数据库服务器
    DATABASE_HOST = 'localhost'

    # 用于链接数据库的用户名
    #    如果此处为空，则默认使用sqlite数据库
    DATABASE_USERNAME = ''

    # 数据库用户密码
    DATABASE_PASSWORD = ''

    # 站点邮件前缀
    MAIL_SUBJECT_PREFIX = ''

    # 站点邮件服务用户名
    EMAIL_USERNAME = ''

    # 站点邮件用户名密码
    EMAIL_PASSWORD = ''

    # 站点邮件服务器设置
    MAIL_SERVER = ''
    MAIL_PORT = 465
    MAIL_USE_SSL = True

    # 下列使用随机生产的数据
    SECRET_KEY = 'NEVERTELLANYBODYEXCEPTIT'

    #  ---------------------------------------------  #
    #  编辑　**以上**　区域以配置您的网站　　　　　　　　　  #
    #  --------------------------------------------   #

    # 通用设置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SITE_INITIATED = False

    def __init__(self, mode):
        # default develop mode
        # 默认开发模式
        if mode == 'default' or mode == 'deve':
            self.DEBUG = True
            db_name = 'data-deve.sqlite'
        # test mode
        # 测试模式
        elif mode == 'test':
            self.TESTING = True
            db_name = 'data-test.sqlite'
        # production mode
        # 生产模式
        else:
            db_name = 'data.sqlite'

        if self.DATABASE_NAME == '':
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, db_name)
        else:
            self.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8' \
                                           % (self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_HOST,
                                              self.DATABASE_NAME)

    @staticmethod
    def init_app(app):
        pass

config = {
    'development': Config('deve'),
    'testing': Config('test'),
    'production': Config('prod'),

    'default': Config('default')
}
