from flask import Blueprint, jsonify, request

main_v1 = Blueprint('main', __name__)


@main_v1.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    return jsonify(json_data)


@main_v1.route('/logout', methods=['POST'])
def logout():
    json_data = request.get_json()
    return jsonify(json_data)


@main_v1.route('/info')
def get_site_info():
    return jsonify(status='ok',
                   page='site info page')


@main_v1.route('/info', methods=['POST'])
def setup_site():
    json_data = request.get_json()
    return jsonify(json_data)
