from flask import Flask
from flask_cors import CORS
from routes.auth import auth_routes
from routes.users import user_routes
from routes.teams import team_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Enable CORS
CORS(app)

# Register Blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(user_routes, url_prefix='/users')
app.register_blueprint(team_routes, url_prefix='/teams')

if __name__ == '__main__':
    app.run(port=5000)
