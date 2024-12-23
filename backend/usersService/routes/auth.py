from flask import Blueprint, request, jsonify
import jwt
import datetime
from functools import wraps
from db_connection import get_db_connection
import bcrypt

# Blueprint for auth routes
auth_routes = Blueprint('auth', __name__)

# Secret key for JWT
SECRET_KEY = 'your_secret_key'  # Replace this with a secure key

# Decorator for requiring a token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1]  # Expected format: "Bearer <token>"
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data  # Attach decoded user info to the request
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

# Function to generate JWT
def generate_token(user_id, team_id=None, is_owner=False, is_admin=False):
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'is_owner': is_owner,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # Token expires in 30 days
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

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
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO `User` (`username`, `email`, `password`)
            VALUES (%s, %s, %s)
        """, (username, email, hashed_password))
        connection.commit()
        user_id = cursor.lastrowid
        token = generate_token(user_id)
        return jsonify({'message': 'User registered successfully!', 'token': token}), 201
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
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, email, password FROM `User` WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            user_id = user[0]
            cursor.execute("""
                SELECT tu.team_id, tu.role_id, t.owner_id 
                FROM `Team_User` tu 
                LEFT JOIN `Team` t ON tu.team_id = t.id
                WHERE tu.user_id = %s
            """, (user_id,))
            team_info = cursor.fetchone()

            team_id = team_info[0] if team_info else None
            is_admin = team_info[1] == 2 if team_info else False
            is_owner = team_info[2] == user_id if team_info else False

            token = generate_token(user_id, team_id, is_owner, is_admin)
            return jsonify({'message': 'Login successful!', 'token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection:
            connection.close()

@auth_routes.route('/refresh', methods=['POST'])
@token_required
def refresh_token():
    user = request.user
    token = generate_token(
        user_id=user['user_id'],
        team_id=user.get('team_id'),
        is_owner=user.get('is_owner'),
        is_admin=user.get('is_admin')
    )
    return jsonify({'token': token}), 200

@auth_routes.route('/protected', methods=['GET'])
@token_required
def protected_route():
    user = request.user
    return jsonify({
        'message': 'Access granted to protected route!',
        'user_id': user['user_id'],
        'team_id': user.get('team_id'),
        'is_owner': user.get('is_owner'),
        'is_admin': user.get('is_admin')
    }), 200
