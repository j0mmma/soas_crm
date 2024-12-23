from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from routes.auth import auth_routes, User
from routes.users import user_routes
from routes.teams import team_routes
from db_connection import get_db_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# User loader for Flask-Login
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
    except Exception as e:
        print(f"Error loading user: {e}")
    finally:
        if connection:
            connection.close()
    return None

# Enable CORS
CORS(app)

# Register Blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(team_routes, url_prefix='/teams')

if __name__ == '__main__':
    app.run(port=5000)
