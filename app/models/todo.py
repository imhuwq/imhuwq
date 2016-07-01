from .. import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = 'tasks'

    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(120), index=True)
    _level = db.Column('level', db.String(2))
    _status = db.Column('status', db.Boolean, default=False)
    _start = db.Column('start', db.DateTime, default=None)
    _finish = db.Column('finish', db.DateTime, default=None)

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        old = Task.query.filter_by(_text=t).filter_by(_status=False).first()
        if old:
            raise AttributeError("Task 已存在")
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

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, s):
        if not isinstance(s, datetime):
            raise AttributeError('开始时间应该是 datetime 对象')
        self._start = s

    @property
    def finish(self):
        return self._finish

    @finish.setter
    def finish(self, f):
        if not isinstance(f, datetime):
            raise AttributeError('完成时间应该是 datetime 对象')
        self._finish = f
