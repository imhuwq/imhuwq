from flask import Blueprint, request
from datetime import datetime
from ..models.todo import Task, Flow, LevelLimitation, DuplicateTaskError, UndefinedTaskLevel, FlowTextTooLong, \
    TaskNotExist, FlowCountOutOfRange
from ..helpers import admin_required, gen_ok_200, gen_err_404, gen_err_500
from .. import db, misaka

ajax_todo = Blueprint('ajax_todo', __name__)

POST = ['GET', 'POST']


@ajax_todo.route('/new-task', methods=POST)
@admin_required
def new_task():
    task_text = request.form.get('task_text')
    task_level = request.form.get('task_level')
    try:
        new = Task(text=task_text, level=task_level, start=datetime.utcnow())
        db.session.add(new)
        db.session.commit()
        return gen_ok_200(id=new.id)
    except (DuplicateTaskError, LevelLimitation, UndefinedTaskLevel) as e:
        db.session.rollback()
        return gen_err_500(e)


@ajax_todo.route('/finish-task', methods=POST)
@admin_required
def finish_task():
    task_id = request.form.get('task_id')
    if task_id:
        task = Task.query.get(task_id)
        task.status = True
        task.finish = datetime.utcnow()
        db.session.commit()
        return gen_ok_200()
    return gen_err_404()


@ajax_todo.route('/delete-task', methods=POST)
@admin_required
def delete_task():
    task_id = request.form.get('id', 0)
    task = Task.query.get(task_id)
    if task:
        task.delete()
        db.session.commit()
        return gen_ok_200()
    return gen_err_404()


@ajax_todo.route('/arrange-task', methods=POST)
@admin_required
def arrange_task():
    new_level = request.form.get('level')
    task_id = request.form.get('id')
    task = Task.query.get(task_id)
    if task_id:
        try:
            task.level = new_level
            db.session.commit()
            return gen_ok_200()
        except (LevelLimitation, UndefinedTaskLevel) as e:
            db.session.rollback()
            return gen_err_500(e)

    return gen_err_404()


@ajax_todo.route('/edit-task', methods=POST)
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
            return gen_ok_200()
        except (DuplicateTaskError, LevelLimitation, UndefinedTaskLevel) as e:
            db.session.rollback()
            return gen_err_500(e)
    return gen_err_404()


@ajax_todo.route('/task-idea', methods=POST)
@admin_required
def edit_idea():
    task_id = request.form.get('id')
    task = Task.query.get(task_id)
    if task:
        task_idea = request.form.get('idea')
        try:
            task.idea = task_idea
            db.session.commit()
            return gen_ok_200(idea=task_idea, html=misaka.render(task_idea))
        except Exception as e:
            db.session.rollback()
            return gen_err_500(e)
    return gen_err_404()


@ajax_todo.route('/new-flow', methods=POST)
@admin_required
def new_flow():
    task_id = request.form.get('task')
    flow_text = request.form.get('flow')
    try:
        flow = Flow(task=task_id, text=flow_text)
        db.session.add(flow)
        db.session.commit()
        return gen_ok_200(id=flow.id, fake_id=flow.fake_id)
    except (FlowTextTooLong, TaskNotExist, FlowCountOutOfRange) as e:
        db.session.rollback()
        return gen_err_500(e)
    except Exception:
        return gen_err_404()


@ajax_todo.route('/flow-order', methods=POST)
@admin_required
def flow_order():
    task_id = request.form.get('task')
    new_order = request.form.get('order')
    task = Task.query.get(task_id)
    if task:
        task.flow_order = new_order
        db.session.commit()
        return gen_ok_200()
    return gen_err_404()


@ajax_todo.route('/edit-flow', methods=POST)
@admin_required
def edit_flow():
    flow_id = request.form.get('id')
    flow = Flow.query.get(flow_id)
    if flow:
        text = request.form.get('text')
        try:
            flow.text = text
            db.session.commit()
            return gen_ok_200()
        except FlowTextTooLong as e:
            return gen_err_500(e)
    return gen_err_404()


@ajax_todo.route('/delete-flow', methods=POST)
@admin_required
def delete_flow():
    flow_id = request.form.get('id')
    flow = Flow.query.get(flow_id)
    if flow:
        flow.delete()
        db.session.commit()
        return gen_ok_200()
    return gen_err_404()
