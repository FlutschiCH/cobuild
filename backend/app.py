from gevent import monkey
monkey.patch_all()

import os
import sys
# Enable gevent support for the debugger (VS Code / debugpy)
os.environ['GEVENT_SUPPORT'] = 'True'

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from config import Config
from models import User
from extensions import db, socketio, oauth
from gevent.pywsgi import WSGIServer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # Configure CORS
    # Allow all origins (regex .*) to support Lovable's dynamic preview URLs with credentials
    CORS(app, resources={r"/*": {"origins": r".*"}}, supports_credentials=True)

    # Initialize SocketIO with the app
    socketio.init_app(app)

    # Initialize OAuth
    oauth.init_app(app)

    # Import and register blueprints
    from auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from chat.routes import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix='/chat')

    from projects.routes import projects as projects_blueprint
    app.register_blueprint(projects_blueprint, url_prefix='/projects')
    
    @app.route('/')
    def index():
        return "CoBuild Server is Running (WSS + HTTPS)"

    # Import socketio handlers
    from ws import handler

    with app.app_context():
        db.create_all()

    return app

app = create_app()

class SSLFilter(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        if "SSLV3_ALERT_CERTIFICATE_UNKNOWN" in data:
            return
        self.stream.write(data)

    def flush(self):
        self.stream.flush()

if __name__ == '__main__':

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)


    cert = os.path.join(PROJECT_ROOT, 'backend', 'certs', 'cert.pem')
    key = os.path.join(PROJECT_ROOT, 'backend', 'certs', 'key.pem')

    # Determine debug mode (default to True for development)
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # use_reloader=False is required to prevent gevent/debugger conflicts on Windows
    # We use a custom log filter to suppress noisy SSL handshake errors from self-signed certs.
    # Using WSGIServer directly avoids argument collisions that occur with socketio.run()
    print("Starting Gevent WSGIServer on https://0.0.0.0:8051")
    http_server = WSGIServer(('0.0.0.0', 8051), app, keyfile=key, certfile=cert, log=SSLFilter(sys.stderr), error_log=SSLFilter(sys.stderr))
    http_server.serve_forever()
