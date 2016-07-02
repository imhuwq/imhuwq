from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models.todo import Task, DuplicateTaskNameError, CountLimitationError
from ..helpers import admin_required
from .. import db

ajax_todo = Blueprint('ajax_todo', __name__)


@ajax_todo.route('/new-task', methods=['GET', 'POST'])
@admin_required
def new_task():
    task_text = request.form.get('task_text')
    task_level = request.form.get('task_level')
    if task_text and task_level:
        try:
            new = Task(text=task_text, level=task_level, start=datetime.utcnow())
            db.session.add(new)
            db.session.commit()
            return jsonify({
                'status': 200,
                'id': new.id
            })
        except DuplicateTaskNameError as e:
            db.session.rollback()
            return jsonify({
                'status': 500,
                'message': e.__str__()
            })
        except CountLimitationError as e:
            db.session.rollback()
            return jsonify({
                'status': 500,
                'message': e.__str__()
            })
    return jsonify({
        'status': 404,
        'message': '创建 Task 失败'
    })


@ajax_todo.route('/finish-task', methods=['GET', 'POST'])
@admin_required
def finish_task():
    task_id = request.form.get('task_id')
    if task_id:
        task = Task.query.get(task_id)
        task.status = True
        task.finish = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'status': 200
        })
    return jsonify({
        'status': 404,
        'message': '操作失败'
    })


@ajax_todo.route('/delete-task', methods=['GET', 'POST'])
@admin_required
def delete_task():
    task_id = request.form.get('id')
    if task_id:
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({
                'status': 200
            })
    return jsonify({
        'status': 400,
        'message': '操作失败'
    })


@ajax_todo.route('/arrange-task', methods=['GET', 'POST'])
@admin_required
def arrange_task():
    new_level = request.form.get('level')
    if new_level not in ['00', '01', '10', '11']:
        return jsonify({
            'status': 400,
            'message': '请输入正确的优先级指标'
        })

    task_id = request.form.get('id')
    task = Task.query.get(task_id)
    if task_id:
        try:
            task.level = new_level
            db.session.commit()
            return jsonify({
                'status': 200,
            })
        except CountLimitationError as e:
            db.session.rollback()
            return jsonify({
                'status': 500,
                'message': e.__str__()
            })

    return jsonify({
        'status': 404,
        'message': '操作失败'
    })


@ajax_todo.route('/edit-task', methods=['GET', 'POST'])
@admin_required
def edit_task():
    task_id = request.form.get('id')
    task = Task.query.get(task_id)
    if task:
        task_text = request.form.get('text')
        task_level = request.form.get('level')
        try:
            task.text = task_text
            task.level = task_level
            db.session.commit()
            return jsonify({
                'status': 200
            })
        except DuplicateTaskNameError as e:
            db.session.rollback()
            return jsonify({
                'status': 500,
                'message': e.__str__()
            })
        except CountLimitationError as e:
            db.session.rollback()
            return jsonify({
                'status': 500,
                'message': e.__str__()
            })
    return jsonify({
        'status': 404,
        'message': "操作失败"
    })
