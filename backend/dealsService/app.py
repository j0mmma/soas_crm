from flask import Flask
from flask_cors import CORS
from controllers.DealController import DealController
from controllers.ContactController import ContactController


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Enable CORS
CORS(app)

# Register Controllers
deal_controller = DealController()
contact_controller = ContactController()

app.register_blueprint(deal_controller.blueprint, url_prefix='/deals')
app.register_blueprint(contact_controller.blueprint, url_prefix='/contacts')


if __name__ == '__main__':
    app.run(port=5001)
