from functools import wraps
from flask import request, jsonify
import jwt

SECRET_KEY = 'your_secret_key' 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1] 
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data 
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated
