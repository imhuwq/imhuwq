from .. import db
from ..helpers import base36, chunk_string
from datetime import datetime


class LevelLimitation(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DuplicateTaskError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UndefinedTaskLevel(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FlowTextTooLong(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TaskNotExist(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FlowCountOutOfRange(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Task(db.Model):
    __tablename__ = 'todo_tasks'

    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(120), index=True)
    _level = db.Column('level', db.String(2))
    _status = db.Column('status', db.Boolean, default=False)
    _start = db.Column('start', db.DateTime, default=None)
    _finish = db.Column('finish', db.DateTime, default=None)
    _idea = db.Column('idea', db.Text)
    _flow_index = db.Column('flow_index', db.Integer, default=0)
    _flow_order = db.Column('flow_order', db.String(150))

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        old = Task.query.filter_by(_text=t, _status=False).first()
        if old:
            raise DuplicateTaskError("Task 已存在")
        self._text = t

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, l):
        if l not in ['11', '10', '01', '00']:
            raise UndefinedTaskLevel("Task Level 必须为 11， 10， 01 和00 四者之一")
        if l == '11':
            count_11 = Task.query.filter_by(_level='11').filter_by(_status=False).count()
            if count_11 >= 2:
                raise LevelLimitation("最多只允许存在两个进行中的 Level 11 Task")
        elif l == '10':
            count_11 = Task.query.filter_by(_level='10').filter_by(_status=False).count()
            if count_11 >= 5:
                raise LevelLimitation("最多只允许存在五个进行中的 Level 10 Task")
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

    @property
    def flows(self):
        fake_ids = chunk_string(self.flow_order, 4)
        all_flows = Flow.query.filter_by(_task=self._id).all()
        sorted_flows = sorted(all_flows, key=lambda flow: fake_ids.index(flow.fake_id))
        return sorted_flows

    @property
    def flow_index(self):
        return self._flow_index or 0

    @flow_index.setter
    def flow_index(self, i):
        self._flow_index = int(i)

    @property
    def flow_order(self):
        return self._flow_order or ''

    @flow_order.setter
    def flow_order(self, o):
        self._flow_order = o

    def delete(self):
        flows = self.flows
        for flow in flows:
            flow.delete(False)
        db.session.delete(self)


class Flow(db.Model):
    __tablename__ = "todo_flow"
    _id = db.Column('id', db.Integer, primary_key=True)
    _text = db.Column('text', db.String(120), index=True)
    _task = db.Column('task', db.Integer, nullable=False)
    _fake_id = db.Column('fake_id', db.String(4))

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        if len(t) > 120:
            raise FlowTextTooLong("Flow 字数超过上限")
        self._text = t

    @property
    def task(self):
        t = Task.query.get(self._task)
        return t

    @task.setter
    def task(self, t_id):
        t = Task.query.get(t_id)
        if t:
            if len(t.flow_order) >= 144:
                raise FlowCountOutOfRange("每个Task最多同时允许36个Step")
            self._task = int(t_id)
            t.flow_index += 1
            fake_id = base36(t.flow_index, 4)
            self._fake_id = fake_id
            t.flow_order += fake_id
        else:
            raise TaskNotExist("Task 不存在")

    @property
    def fake_id(self):
        return self._fake_id

    def delete(self, delete_flow_order=True):
        if delete_flow_order:
            task = self.task
            task.flow_order = task.flow_order.replace(self._fake_id, '')
        db.session.delete(self)
