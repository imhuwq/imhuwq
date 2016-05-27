# -*- coding: utf8 -*-
"""
    app
    ~~~~~~~~~~

    app插件初始化以及app格式化

    关于app文档结构:
    ----app
        ----__init__.py (本文件)
        ----forms.py
        ----models.py
        ----views
            ----main.py
            ----blog.py
            ----admin.py
        ----templates
            ----main
            ----blog
            ----admin
        ----static
            ----main
            ----blog
            ----admin
        ----ajax
            ----admin.py

    ----config.py   (配置文件)
    ----tests       (测试模块)
    ----manage.py   (调试,测试,shell)
    ----run.py      (开启应用, 生产环境)
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.misaka import Misaka
from flask.ext.moment import Moment
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
misaka = Misaka(
    fenced_code=True,
    underline=True,
    highlight=True,
    disable_indented_code=True,
    space_headers=True,
    strikethrough=True,
    footnotes=True,
    tables=True,
    math=True)
moment = Moment()

login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'


def create_app(mode='default'):
    app = Flask(__name__)
    con = config[mode]
    app.config.from_object(con)
    con.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    misaka.init_app(app)
    moment.init_app(app)

    # bootstrap使用cdn.bootcss.com提供cdn加快国内访问速度
    from flask_bootstrap import WebCDN
    cdns = app.extensions['bootstrap']['cdns']
    cdns['bootstrap'] = WebCDN('//cdn.bootcss.com/bootstrap/3.3.5/')
    cdns['jquery'] = WebCDN('//cdn.bootcss.com/jquery/1.11.3/')
    cdns['html5shiv'] = WebCDN('//cdn.bootcss.com/html5shiv/3.7.2/')
    cdns['respond.js'] = WebCDN('//cdn.bootcss.com/bootstrap/3.3.5/js/')

    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.views.blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint, url_prefix='/blog')

    from app.views.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.ajax.admin import ajax_admin as ajax_admin_blueprint
    app.register_blueprint(ajax_admin_blueprint, url_prefix='/ajax-admin')

    return app
