import os
import random

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def gen_secret_key(length=50):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789~(-_=+)'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


class Config:
    #  ---------------------------------------------   #
    #  编辑以下区域以配置您的网站　　　　　　　　　　　　　　 #
    #  ---------------------------------------------  #

    # 使用该邮箱注册的用户将成为本站管理员
    SITE_ADMIN_EMAIL = 'email@somebody.com'

    # 数据库名称
    DATABASE_NAME = 'u_db_name'

    # 数据库服务器
    DATABASE_HOST = 'localhost'

    # 用于链接数据库的用户名
    #    如果此处为空，则默认使用sqlite数据库
    DATABASE_USERNAME = 'u_db_un'

    # 数据库用户密码
    DATABASE_PASSWORD = 'u_db_pw'

    #  ---------------------------------------------  #
    #  编辑　**以上**　区域以配置您的网站　　　　　　　　　  #
    #  --------------------------------------------   #

    #  ---------------------------------------------  #
    #  请不要编辑以下区域                　　　　　　　　  #
    #  --------------------------------------------   #

    # 通用设置
    SECRET_KEY = gen_secret_key()

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SITE_INITIATED = False

    def __init__(self, mode):
        # 默认生产模式
        if mode == 'prod' or mode == 'default':
            db_name = 'data-prod.sqlite'

        # 测试模式
        elif mode == 'test':
            self.TESTING = True
            db_name = 'data-test.sqlite'

        # 开发模式
        else:
            self.DEBUG = True
            db_name = 'data-debug.sqlite'

        # 不提供数据库名则使用 sqlite
        if self.DATABASE_NAME == '' or mode == 'test':
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, db_name)

        # 否则使用 postgresql
        else:
            self.SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s/%s' \
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
