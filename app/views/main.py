from flask import Blueprint, render_template, redirect, url_for, current_app

app = Blueprint('app', __name__)


@app.route('/')
def index():
    if current_app.config['DEBUG'] or current_app.config['TESTING']:
        return redirect(url_for('main.config'))
    return render_template('main/index.html')


@app.route('/config')
def config():
    return render_template('main/config.html')
