"""Tests for device endpoints and authorization."""


def _register(client, name="DEV-01"):
    return client.post(
        "/api/client/register",
        json={"device_name": name, "hostname": name.lower()},
    ).get_json()


def test_list_devices_requires_auth(client):
    res = client.get("/api/devices")
    assert res.status_code == 401


def test_list_devices_with_auth(client, auth_headers):
    _register(client, "DEV-01")
    res = client.get("/api/devices", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.get_json()["data"]) >= 1


def test_get_device_not_found(client, auth_headers):
    res = client.get("/api/devices/99999", headers=auth_headers)
    assert res.status_code == 404


def test_viewer_can_read_devices(client, viewer_token):
    _register(client, "DEV-02")
    res = client.get(
        "/api/devices", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res.status_code == 200