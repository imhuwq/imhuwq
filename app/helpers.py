from functools import wraps
from flask_login import current_user
from flask import abort, redirect, url_for, jsonify


def admin_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_administrator:
            abort(404)
        return func(*args, **kwargs)

    return decorator


def base36(num, width=4):
    table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while num > 0:
        rem = num % 36
        num //= 36
        result = table[rem] + result
    length = len(result)
    if length < width:
        result = (width - length) * '0' + result
    return result


def chunk_string(string, width):
    import re
    return re.findall(r'.{%d}' % width, string)


def gen_ok_200(**kwargs):
    data = {'status': 200}
    for kwarg, value in kwargs.items():
        data[kwarg] = value
    return jsonify(data)


def gen_err_404():
    return jsonify({'status': 404,
                    'message': '所操作的Task不存在'})


def gen_err_500(e):
    return jsonify({'status': 500,
                    'message': e.__str__()
                    })

