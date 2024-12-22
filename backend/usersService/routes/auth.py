from flask import Blueprint, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from db_connection import get_db_connection
import bcrypt

# Initialize Blueprint
auth_routes = Blueprint('auth', __name__)

# Initialize LoginManager
login_manager = LoginManager()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    try:
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, email FROM `User` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                return User(id=user[0], username=user[1], email=user[2])
    except Exception as err:
        print(f"Error: {err}")
    finally:
        if connection:
            connection.close()
    return None

@auth_routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO `User` (`username`, `email`, `password`)
                VALUES (%s, %s, %s)
            """, (username, email, hashed_password))
            connection.commit()
            return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection:
            connection.close()

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    email = data.get('email')
    password = data.get('password')

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, email, password FROM `User` WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                user_obj = User(id=user[0], username=user[1], email=user[2])
                login_user(user_obj)
                return jsonify({'message': 'Login successful!', 'user_id': user[0], 'username': user[1]}), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection:
            connection.close()

@auth_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully!'})
