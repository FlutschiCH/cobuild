from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth
from config import Config

db = SQLAlchemy()

# Define allowed origins for CORS to support credentials properly.
# Wildcard "*" is not allowed when credentials are sent.
origins = [
    Config.LOVABLE_FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

socketio = SocketIO(async_mode='gevent', cors_allowed_origins=origins, engineio_logger=True, path='/ws')
oauth = OAuth()
