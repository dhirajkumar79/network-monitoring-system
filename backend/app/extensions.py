from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# async_mode="threading" works without extra dependencies (no eventlet/gevent needed)
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")