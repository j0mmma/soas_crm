from flask import Flask
from flask_cors import CORS
from controllers.AuthController import AuthController
from controllers.UserController import UserController
from controllers.TeamController import TeamController
from ServiceRegistry import ServiceRegistry
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

CORS(app)

auth_controller = AuthController()
user_controller = UserController()
team_controller = TeamController()

app.register_blueprint(auth_controller.blueprint, url_prefix='/auth')
app.register_blueprint(user_controller.blueprint, url_prefix='/users')
app.register_blueprint(team_controller.blueprint, url_prefix='/teams')

SERVICE_NAME = "usersService"
SERVICE_VERSION = "v1.0.0"
SERVICE_URL = "http://localhost:5000"
service_registry = ServiceRegistry(SERVICE_NAME, SERVICE_VERSION, SERVICE_URL)

if service_registry.register_service():
    print(f"Service '{SERVICE_NAME}' registered and marked as running.")

atexit.register(service_registry.deregister_service)



if __name__ == '__main__':
    app.run(port=5000)
