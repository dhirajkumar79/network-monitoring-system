"""Tests for remote session endpoints and ADMIN-only authorization."""


def _register_and_heartbeat(client, name="RDP-PC"):
    reg = client.post(
        "/api/client/register",
        json={"device_name": name, "hostname": name.lower()},
    ).get_json()
    token = reg["data"]["device_token"]
    device_id = reg["data"]["device_id"]

    client.post(
        "/api/client/heartbeat",
        json={"cpu_usage": 10.0},
        headers={"X-Device-Token": token},
    )
    return device_id


def test_list_sessions_requires_auth(client):
    res = client.get("/api/sessions")
    assert res.status_code == 401


def test_list_sessions_with_auth(client, auth_headers):
    res = client.get("/api/sessions", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"] == []


def test_create_session_as_admin(client, auth_headers):
    device_id = _register_and_heartbeat(client, "RDP-01")
    res = client.post(
        "/api/sessions",
        json={"device_id": device_id, "session_type": "REMOTE_DESKTOP"},
        headers=auth_headers,
    )
    assert res.status_code == 201
    body = res.get_json()["data"]
    assert body["connection_status"] == "CONNECTING"
    assert body["session_type"] == "REMOTE_DESKTOP"


def test_viewer_cannot_create_session(client, viewer_token):
    device_id = _register_and_heartbeat(client, "RDP-02")
    res = client.post(
        "/api/sessions",
        json={"device_id": device_id, "session_type": "REMOTE_DESKTOP"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403


def test_session_on_offline_device_fails(client, auth_headers, app):
    """Sessions can only be created for ONLINE devices."""
    from app.extensions import db
    from app.models.device import Device

    # Register a device (defaults to ONLINE)
    reg = client.post(
        "/api/client/register",
        json={"device_name": "OFFLINE-PC", "hostname": "offline-pc"},
    ).get_json()
    device_id = reg["data"]["device_id"]

    # Force it OFFLINE to simulate the case
    device = db.session.get(Device, device_id)
    device.status = "OFFLINE"
    db.session.commit()

    # Now the session request should fail
    res = client.post(
        "/api/sessions",
        json={"device_id": device_id, "session_type": "REMOTE_DESKTOP"},
        headers=auth_headers,
    )
    assert res.status_code == 400
    assert "online" in res.get_json()["message"].lower()


def test_end_session(client, auth_headers):
    device_id = _register_and_heartbeat(client, "RDP-END")
    create = client.post(
        "/api/sessions",
        json={"device_id": device_id, "session_type": "REMOTE_DESKTOP"},
        headers=auth_headers,
    ).get_json()
    sid = create["data"]["session_id"]

    res = client.post(f"/api/sessions/{sid}/end", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["data"]["connection_status"] == "DISCONNECTED"
    assert res.get_json()["data"]["end_time"] is not None


def test_agent_pending_session_polling(client, auth_headers):
    reg = client.post(
        "/api/client/register",
        json={"device_name": "POLL-PC", "hostname": "poll-pc"},
    ).get_json()
    token = reg["data"]["device_token"]
    device_id = reg["data"]["device_id"]

    client.post(
        "/api/client/heartbeat",
        json={"cpu_usage": 10.0},
        headers={"X-Device-Token": token},
    )

    client.post(
        "/api/sessions",
        json={"device_id": device_id, "session_type": "REMOTE_DESKTOP"},
        headers=auth_headers,
    )

    res = client.get(
        "/api/client/pending-session",
        headers={"X-Device-Token": token},
    )
    assert res.status_code == 200
    assert res.get_json()["data"] is not None
    assert res.get_json()["data"]["connection_status"] == "CONNECTING"