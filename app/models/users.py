from flask_sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from .setting import Settings


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    __password = db.String(db.String)

    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.__password = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self.__password, password)

    def is_admin(self):
        settings = Settings.query.first()
        admin_email = settings.site_admin_email
        return self.email == admin_email


@event.listens_for(Users, 'after_update')
def update_admin_email(mapper, connection, target):
    if target.is_admin():
        settings = Settings.query.first()
        settings.site_admin_email = target.email
