# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CsrfProtect

from config import Config

config = Config()
db = SQLAlchemy()
login = LoginManager()


def create_app(mode='production'):
    app = Flask(__name__)
    app.mode = mode

    config.init_app(app)
    db.init_app(app)
    login.init_app(app)

    if mode == 'production':
        csrf = CsrfProtect()
        csrf.init_app(app)

    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.api_v1.main import main_v1 as api_v1_main
    app.register_blueprint(api_v1_main, url_prefix='/api/v1')

    from app.api_v1.blog import blog_v1 as api_v1_blog
    app.register_blueprint(api_v1_blog, url_prefix='/api/v1/blog')

    return app
