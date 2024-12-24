from flask import Flask
from flask_cors import CORS
from controllers.AuthController import AuthController
from controllers.UserController import UserController
from controllers.TeamController import TeamController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Enable CORS
CORS(app)

# Initialize Controllers
auth_controller = AuthController()
user_controller = UserController()
team_controller = TeamController()

# Register Blueprints
app.register_blueprint(auth_controller.blueprint, url_prefix='/auth')
app.register_blueprint(user_controller.blueprint, url_prefix='/users')
app.register_blueprint(team_controller.blueprint, url_prefix='/teams')

if __name__ == '__main__':
    app.run(port=5000)
