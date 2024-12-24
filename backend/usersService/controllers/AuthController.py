from flask import Blueprint, request, jsonify
from models.User import User
import jwt
import datetime
from .utils import token_required
from functools import wraps
from models.Team import Team


class AuthController:
    SECRET_KEY = 'your_secret_key'  # Replace with a secure key

    def __init__(self):
        self.blueprint = Blueprint('auth', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule('/signup', 'signup', self.signup, methods=['POST'])
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.blueprint.add_url_rule('/refresh', 'refresh_token', self.refresh_token, methods=['POST'])
        self.blueprint.add_url_rule('/protected', 'protected', self.protected_route, methods=['GET'])

    def generate_token(self, user_id, team_id=None, is_owner=False, is_admin=False):
        """Generate JWT token with user data."""
        payload = {
            'user_id': user_id,
            'team_id': team_id,
            'is_owner': is_owner,
            'is_admin': is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # Token expires in 30 days
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        return token

    def signup(self):
        """Handle user signup."""
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid JSON payload'}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        try:
            user = User(username=username, email=email, password=password)
            user.save()  # Save the user using the User model's `save` method

            # Generate JWT token
            token = self.generate_token(user.id)
            return jsonify({'message': 'User registered successfully!', 'token': token}), 201
        except Exception as err:
            return jsonify({'error': str(err)}), 500

    def login(self):
        """Handle user login."""
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid JSON payload'}), 400

        email = data.get('email')
        password = data.get('password')

        try:
            user = User.authenticate(email, password)  # Authenticate user
            if not user:
                return jsonify({'message': 'Invalid credentials'}), 401

            # Fetch additional team info using Team model
            team_info = Team.get_team_info_by_user_id(user.id)

            if team_info:
                team_id = team_info.team_id
                is_owner = team_info.owner_id == user.id
                is_admin = any(member['role_id'] == 2 for member in Team.get_team_members(team_id) if member['user_id'] == user.id)
            else:
                team_id = None
                is_owner = False
                is_admin = False

            token = self.generate_token(user.id, team_id, is_owner, is_admin)
            return jsonify({'message': 'Login successful!', 'token': token}), 200
        except Exception as err:
            return jsonify({'error': str(err)}), 500


    @token_required
    def refresh_token(self):
        """Refresh JWT token."""
        user = request.user
        token = self.generate_token(
            user_id=user['user_id'],
            team_id=user.get('team_id'),
            is_owner=user.get('is_owner'),
            is_admin=user.get('is_admin')
        )
        return jsonify({'token': token}), 200

    @token_required
    def protected_route(self):
        """Example protected route."""
        user = request.user
        return jsonify({
            'message': 'Access granted to protected route!',
            'user_id': user['user_id'],
            'team_id': user.get('team_id'),
            'is_owner': user.get('is_owner'),
            'is_admin': user.get('is_admin')
        }), 200
