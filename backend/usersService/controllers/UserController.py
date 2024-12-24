from flask import Blueprint, request, jsonify
from models.User import User
from functools import wraps
from .utils import token_required

class UserController:
    def __init__(self):
        self.blueprint = Blueprint('users', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule('/', 'get_all_users', self.get_all_users, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'get_user_by_id', self.get_user_by_id, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'update_user', self.update_user, methods=['PUT'])

    @token_required
    def get_all_users(self):
        try:
            users = User.get_all_users()
            return jsonify(users), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def get_user_by_id(self, user_id):
        try:
            user = User.get_user_by_id(user_id)
            return jsonify(user.__dict__), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def update_user(self, user_id):
        current_user_id = request.user['user_id']
        if current_user_id != user_id:
            return jsonify({'message': 'Unauthorized to update this user!'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid JSON payload'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username and not email and not password:
            return jsonify({'message': 'No fields to update'}), 400

        try:
            user = User.get_user_by_id(user_id)
            user.update(username=username, email=email, password=password)
            return jsonify({'message': 'User updated successfully!'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
