from config import config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_misaka import Misaka
from flask_moment import Moment
from flask_wtf.csrf import CsrfProtect

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
csrf = CsrfProtect()

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
    csrf.init_app(app)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    # bootstrap使用本地文件
    from flask_bootstrap import WebCDN
    cdns = app.extensions['bootstrap']['cdns']
    cdns['bootstrap'] = WebCDN('/static/bootstrap/')
    cdns['jquery'] = WebCDN('/static/jquery/')

    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.views.blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint, url_prefix='/blog')

    from app.views.todo import todo as todo_blueprint
    app.register_blueprint(todo_blueprint, url_prefix='/todo')

    from app.ajaxs.todo import ajax_todo as ajax_todo_blueprint
    app.register_blueprint(ajax_todo_blueprint, url_prefix='/ajax-todo')

    from app.views.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.ajaxs.admin import ajax_admin as ajax_admin_blueprint
    app.register_blueprint(ajax_admin_blueprint, url_prefix='/ajax-admin')

    return app


    # TODO: 找回密码
    # TODO： 导出PDF
