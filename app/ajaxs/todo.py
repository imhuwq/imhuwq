from flask import Blueprint, request, jsonify
from ..models.todo import Task
from ..helpers import admin_required
from .. import db

ajax_todo = Blueprint('ajax_todo', __name__)


@ajax_todo.route('/new-task', methods=['GET', 'POST'])
@admin_required
def new_task():
    task_text = request.form.get('task_text')
    task_level = request.form.get('task_level')
    if task_text and task_level:
        new = Task(text=task_text, level=task_level)
        db.session.add(new)
        db.session.commit()
        return jsonify({
            'status': 200,
            'id': new.id
        })
    return jsonify({
        'status': 400
    })


@ajax_todo.route('/finish-task', methods=['GET', 'POST'])
@admin_required
def finish_task():
    task_id = request.form.get('task_id')
    if task_id:
        task = Task.query.get(task_id)
        task.status = True
        db.session.commit()
        return jsonify({
            'status': 200
        })
    return jsonify({
        'status': 400
    })
