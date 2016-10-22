from flask import Blueprint, render_template, jsonify

main = Blueprint('app', __name__)


@main.route('/')
def index():
    return jsonify(status='ok',
                   page='home page to load static files')


@main.route('/config')
def config():
    return render_template('main/config.html')
