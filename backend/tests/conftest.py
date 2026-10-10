"""Pytest fixtures shared across tests."""

import os
import sys

import pytest

# Ensure `app` package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db as _db


class TestConfig:
    """Test configuration: use SQLite in-memory for speed and isolation."""

    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = "http://localhost:5173"
    HEARTBEAT_TIMEOUT_SECONDS = 60
    DEBUG = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    from app.models.user import User

    u = User(username="testadmin", role="ADMIN", is_active=True, email=None)
    u.set_password("testpass123")
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def viewer_user(app):
    from app.models.user import User

    u = User(username="testviewer", role="VIEWER", is_active=True, email=None)
    u.set_password("testpass123")
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def admin_token(client, admin_user):
    res = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    return res.get_json()["data"]["access_token"]


@pytest.fixture
def viewer_token(client, viewer_user):
    res = client.post(
        "/api/auth/login",
        json={"username": "testviewer", "password": "testpass123"},
    )
    return res.get_json()["data"]["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}