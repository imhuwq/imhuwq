from flask import Blueprint, jsonify

main = Blueprint('main', __name__)


@main.route('/')
def get():
    return jsonify(status='ok')
