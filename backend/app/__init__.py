from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, jwt, socketio


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Init extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)

    # --- CORS ---
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*").split(","))

    # --- Import models so migrations can see them ---
    from app import models  # noqa: F401

    # --- Register blueprints ---
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.client import client_bp
    from app.routes.devices import devices_bp
    from app.routes.events import events_bp
    from app.routes.sessions import sessions_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(sessions_bp)

    # --- Register Socket.IO handlers ---
    from app.websocket.events import register_socketio_handlers
    register_socketio_handlers()

    # --- Start background tasks ---
    from app.tasks.offline_checker import start_offline_checker
    start_offline_checker(app)

    return app