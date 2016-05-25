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

    #  ---------------------------------------------  #
    #  编辑　**以上**　区域以配置您的网站　　　　　　　　　  #
    #  --------------------------------------------   #

    # global configurations
    # 通用设置
    SECRET_KEY = ''
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SITE_INITIATED = False

    def __init__(self, mode):
        # 默认开发模式
        if mode == 'prod' or mode == 'default':
            db_name = 'data.sqlite'

        # 测试模式
        elif mode == 'test':
            self.TESTING = True
            db_name = 'data-test.sqlite'

        # 生产模式
        elif mode == 'debug':
            self.DEBUG = True
            db_name = 'data-debug.sqlite'

        if self.DATABASE_NAME == '' or mode == 'test':
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, db_name)
        else:
            self.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8' \
                                           % (self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_HOST,
                                              self.DATABASE_NAME)

    @staticmethod
    def init_app(app):
        pass


config = {
    'prod': Config('prod'),
    'test': Config('test'),
    'debug': Config('debug'),
    'default': Config('default')
}
