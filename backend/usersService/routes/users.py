from flask import Blueprint, request, jsonify
from .auth import token_required  # Import the token_required decorator
from db_connection import get_db_connection
import bcrypt

user_routes = Blueprint('users', __name__)

# Get all users
@user_routes.route('/', methods=['GET'])
@token_required
def get_all_users():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM `User`")
        users = cursor.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# Get user by ID
@user_routes.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id(user_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM `User` WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return jsonify(user), 200
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# TODO: user can only chage their data
# Update user details
@user_routes.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    current_user_id = request.user['user_id']  # Access user data from token
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

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = "UPDATE `User` SET "
        params = []

        if username:
            query += "`username` = %s, "
            params.append(username)
        if email:
            query += "`email` = %s, "
            params.append(email)
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query += "`password` = %s, "
            params.append(hashed_password)

        query = query.rstrip(', ')  # Remove trailing comma
        query += " WHERE `id` = %s"
        params.append(user_id)

        cursor.execute(query, tuple(params))
        connection.commit()
        return jsonify({'message': 'User updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()
