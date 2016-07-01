from flask import Blueprint, render_template
from ..helpers import admin_required
from ..models.todo import Task
from datetime import datetime
from sqlalchemy import or_

todo = Blueprint('todo', __name__)


@todo.route('/')
@admin_required
def index():
    title = 'ToDo'
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    tasks = Task.query.filter(or_(Task._finish > today,
                                  Task._finish == None)) \
                      .order_by(Task._level.desc())\
                      .order_by(Task._start.asc()).all()

    return render_template('todo/index.html',
                           title=title,
                           tasks=tasks)
