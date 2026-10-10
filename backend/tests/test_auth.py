"""Tests for authentication endpoints."""


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_login_success(client, admin_user):
    res = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "password_hash" not in body["data"]["user"]


def test_login_wrong_password(client, admin_user):
    res = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "wrongpass"},
    )
    assert res.status_code == 401
    assert res.get_json()["success"] is False


def test_login_missing_fields(client):
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400


def test_me_with_token(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["username"] == "testadmin"


def test_me_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_invalid_token(client):
    res = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert res.status_code == 422