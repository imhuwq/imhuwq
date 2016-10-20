from flask import Blueprint, jsonify

blog = Blueprint('blog', __name__)


@blog.route('/')
def get():
    return jsonify(status='ok')

