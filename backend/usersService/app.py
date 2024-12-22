from flask import Flask
from flask_cors import CORS
from routes.auth import auth_routes, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

CORS(app)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')

if __name__ == '__main__':
    app.run(port=5000)