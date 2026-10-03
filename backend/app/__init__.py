from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Init extensions ---
    db.init_app(app)
    migrate.init_app(app, db)

    # CORS: allow the React frontend (localhost:5173) to talk to us later
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*").split(","))

    # --- Import models so migrations can see them ---
    from app import models  # noqa: F401

    # --- Register blueprints ---
    from app.routes.health import health_bp

    app.register_blueprint(health_bp)

    return app