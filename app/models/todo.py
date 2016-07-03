from .. import db
from datetime import datetime


class CountLimitationError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DuplicateTaskNameError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Task(db.Model):
    __tablename__ = 'tasks'

    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(120), index=True)
    _level = db.Column('level', db.String(2))
    _status = db.Column('status', db.Boolean, default=False)
    _start = db.Column('start', db.DateTime, default=None)
    _finish = db.Column('finish', db.DateTime, default=None)
    _idea = db.Column('idea', db.Text)
    notes = db.relationship('Note', backref='task', lazy='dynamic')

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
            raise DuplicateTaskNameError("Task 已存在")
        self._text = t

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, l):
        if l == '11':
            count_11 = Task.query.filter_by(_level='11').filter_by(_status=False).count()
            if count_11 >= 2:
                raise CountLimitationError("最多只允许存在两个进行中的 Level 11 Task")
        elif l == '10':
            count_11 = Task.query.filter_by(_level='10').filter_by(_status=False).count()
            if count_11 >= 5:
                raise CountLimitationError("最多只允许存在五个进行中的 Level 10 Task")
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

    @property
    def idea(self):
        return self._idea

    @idea.setter
    def idea(self, i):
        self._idea = i


class Note(db.Model):
    __tablename__ = 'notes'

    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(60), index=True)
    _status = db.Column('status', db.Boolean, default=False)
    _color = db.Column('color', db.String(1), default='W')
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        if len(t) > 60:
            raise AttributeError('文本过长')
        self._text = t

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, s):
        self._status = s

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        if c not in ['W', 'R', 'Y', 'B']:
            raise AttributeError('仅允许 W， R， Y， B四种颜色标志')
        self._color = c
