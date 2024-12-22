from flask import Flask
from flask_cors import CORS
from routes.auth import auth_routes
from routes.auth import login_manager

from routes.users import user_routes
from routes.teams import team_routes
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login' 
CORS(app)

# Register Blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(team_routes, url_prefix='/teams')


if __name__ == '__main__':
    app.run(port=5000)
