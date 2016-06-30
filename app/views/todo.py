from flask import Blueprint, render_template
from ..helpers import admin_required
from ..models.todo import Task

todo = Blueprint('todo', __name__)


@todo.route('/')
@admin_required
def index():
    title = 'ToDo'
    tasks_11 = Task.query.filter_by(_status=False).filter_by(_level='11').all()
    tasks_10 = Task.query.filter_by(_status=False).filter_by(_level='10').all()
    tasks_01 = Task.query.filter_by(_status=False).filter_by(_level='01').all()
    tasks_00 = Task.query.filter_by(_status=False).filter_by(_level='00').all()

    return render_template('todo/index.html',
                           title=title,
                           tasks_11=tasks_11,
                           tasks_10=tasks_10,
                           tasks_01=tasks_01,
                           tasks_00=tasks_00)
