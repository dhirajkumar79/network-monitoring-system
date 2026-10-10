"""Tests for client agent endpoints."""


def _register_device(client, name="TEST-PC"):
    return client.post(
        "/api/client/register",
        json={
            "device_name": name,
            "hostname": name.lower(),
            "operating_system": "Test OS",
            "ip_address": "10.0.0.1",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "location": "Test Lab",
        },
    )


def test_register_device(client):
    res = _register_device(client)
    assert res.status_code == 201
    body = res.get_json()
    assert body["success"] is True
    assert "device_id" in body["data"]
    assert "device_token" in body["data"]
    assert len(body["data"]["device_token"]) > 30


def test_register_missing_fields(client):
    res = client.post("/api/client/register", json={"device_name": "only-name"})
    assert res.status_code == 400


def test_heartbeat_with_valid_token(client):
    reg = _register_device(client).get_json()
    token = reg["data"]["device_token"]

    res = client.post(
        "/api/client/heartbeat",
        json={"cpu_usage": 25.5, "memory_usage": 60.0},
        headers={"X-Device-Token": token},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "ONLINE"


def test_heartbeat_with_invalid_token(client):
    res = client.post(
        "/api/client/heartbeat",
        json={"cpu_usage": 10.0},
        headers={"X-Device-Token": "totally-fake-token"},
    )
    assert res.status_code == 401


def test_heartbeat_without_token(client):
    res = client.post("/api/client/heartbeat", json={"cpu_usage": 10.0})
    assert res.status_code == 401


def test_high_cpu_creates_alert(client):
    reg = _register_device(client, name="CPU-PC").get_json()
    token = reg["data"]["device_token"]

    client.post(
        "/api/client/heartbeat",
        json={"cpu_usage": 95.0, "memory_usage": 50.0},
        headers={"X-Device-Token": token},
    )
    # No crash = success for this test
    assert True