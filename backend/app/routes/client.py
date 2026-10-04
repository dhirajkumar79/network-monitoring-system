import hashlib
import secrets
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.device import Device
from app.models.event import Event
from app.models.metric import NetworkMetric

client_bp = Blueprint("client_bp", __name__)


# ---------- Helpers ----------

def _hash_token(token: str) -> str:
    """SHA-256 hash of the token. We only store the hash, never the token itself."""
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_token() -> str:
    """Cryptographically strong, unpredictable device token."""
    return secrets.token_urlsafe(48)


def _device_from_request():
    """Read X-Device-Token header and return the matching Device, or None."""
    token = request.headers.get("X-Device-Token", "").strip()
    if not token:
        return None
    return Device.query.filter_by(device_token_hash=_hash_token(token)).first()


# ---------- Registration ----------

@client_bp.route("/api/client/register", methods=["POST"])
def register():
    """Register a new device. Returns a device token that the client must
    present on every heartbeat.

    Request JSON:
        {
          "device_name": "LAB-PC-01",
          "hostname": "lab-pc-01",
          "operating_system": "Windows 11",
          "ip_address": "192.168.1.50",
          "mac_address": "AA:BB:CC:DD:EE:FF",
          "location": "Lab 1"
        }
    """
    data = request.get_json(silent=True) or {}

    device_name = (data.get("device_name") or "").strip()
    hostname = (data.get("hostname") or "").strip()

    if not device_name or not hostname:
        return jsonify({
            "success": False,
            "message": "device_name and hostname are required"
        }), 400

    token = _generate_token()

    device = Device(
        device_name=device_name,
        hostname=hostname,
        operating_system=data.get("operating_system"),
        ip_address=data.get("ip_address"),
        mac_address=data.get("mac_address"),
        location=data.get("location"),
        status="ONLINE",
        last_active_time=datetime.utcnow(),
        device_token_hash=_hash_token(token),
    )
    db.session.add(device)
    db.session.flush()  # get device_id

    db.session.add(Event(
        device_id=device.device_id,
        event_type="DEVICE_REGISTERED",
        severity="LOW",
        description=f"Device '{device_name}' registered",
    ))
    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "device_id": device.device_id,
            "device_token": token,  # shown ONCE — client must save it
        },
    }), 201


# ---------- Heartbeat ----------

@client_bp.route("/api/client/heartbeat", methods=["POST"])
def heartbeat():
    """Update last_active_time, set status=ONLINE, and optionally store metrics.

    Headers:
        X-Device-Token: <token>
    Body (all optional except none):
        {
          "cpu_usage": 12.3,
          "memory_usage": 45.6,
          "disk_usage": 67.8,
          "network_upload": 1234.5,
          "network_download": 5678.9,
          "latency_ms": 12.4,
          "packet_loss": 0.0
        }
    """
    device = _device_from_request()
    if device is None:
        return jsonify({"success": False, "message": "Invalid or missing device token"}), 401

    was_offline = device.status != "ONLINE"

    device.last_active_time = datetime.utcnow()
    device.status = "ONLINE"

    if was_offline:
        db.session.add(Event(
            device_id=device.device_id,
            event_type="DEVICE_ONLINE",
            severity="LOW",
            description=f"Device '{device.device_name}' is back online",
        ))

       # Store metrics if provided
    data = request.get_json(silent=True) or {}
    metric = NetworkMetric(
        device_id=device.device_id,
        timestamp=datetime.utcnow(),
        latency_ms=data.get("latency_ms"),
        cpu_usage=data.get("cpu_usage"),
        memory_usage=data.get("memory_usage"),
        disk_usage=data.get("disk_usage"),
        network_upload=data.get("network_upload"),
        network_download=data.get("network_download"),
        packet_loss=data.get("packet_loss"),
    )
    db.session.add(metric)
    db.session.flush()  # flush so alerts can be added in the same commit

    # --- Threshold alerting ---
    from app.services.alert_service import evaluate_alerts
    alert_count = evaluate_alerts(device.device_id, data)
    if alert_count:
        print(f"[alert] {alert_count} alert(s) for device {device.device_id}")

    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "device_id": device.device_id,
            "status": device.status,
            "server_time": datetime.utcnow().isoformat(),
        },
    }), 200