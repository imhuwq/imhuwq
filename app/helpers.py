from functools import wraps
from flask.ext.login import current_user
from flask import abort, redirect, url_for


def admin_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))
        if not current_user.is_administrator:
            abort(403)
        return func(*args, **kwargs)
    return decorator
