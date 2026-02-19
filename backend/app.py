import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager
from .config import Config
from .models import db, User

# Initialize SocketIO
socketio = SocketIO(async_mode='gevent', cors_allowed_origins="*", engineio_logger=True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Configure CORS
    CORS(app, resources={r"/*": {"origins": Config.LOVABLE_FRONTEND_URL}}, supports_credentials=True)

    # Initialize SocketIO with the app
    socketio.init_app(app)

    # Import and register blueprints
    from .auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .chat.routes import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix='/chat')

    from .projects.routes import projects as projects_blueprint
    app.register_blueprint(projects_blueprint, url_prefix='/projects')
    
    # Import socketio handlers
    from .ws import handler

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
