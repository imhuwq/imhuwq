from .. import db


class Task(db.Model):
    __tablename__ = 'tasks'

    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(120), index=True)
    _level = db.Column('level', db.String(2))
    _status = db.Column('status', db.Boolean, default=False)

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        self._text = t

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, l):
        self._level = l

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, s):
        self._status = s
