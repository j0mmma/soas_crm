from flask import Flask
from flask_cors import CORS
from controllers.DealController import DealController
from controllers.ContactController import ContactController
from controllers.TaskController import TaskController
from ServiceSegistry import ServiceRegistry

import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Enable CORS
CORS(app)

# Register Controllers
deal_controller = DealController()
contact_controller = ContactController()
task_controller = TaskController()

app.register_blueprint(deal_controller.blueprint, url_prefix='/deals')
app.register_blueprint(contact_controller.blueprint, url_prefix='/contacts')
app.register_blueprint(task_controller.blueprint, url_prefix='/tasks')

SERVICE_NAME = "dealService"
SERVICE_VERSION = "v1.0.0"
SERVICE_URL = "http://localhost:5001"
service_registry = ServiceRegistry(SERVICE_NAME, SERVICE_VERSION, SERVICE_URL)


# Register service on startup
if service_registry.register_service():
    print(f"Service '{SERVICE_NAME}' registered and marked as running.")

# Deregister service on shutdown
atexit.register(service_registry.deregister_service)


if __name__ == '__main__':
    app.run(port=5001)
