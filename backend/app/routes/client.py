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
    db.session.flush()
    db.session.add(Event(
        device_id=device.device_id,
        event_type="DEVICE_REGISTERED",
        severity="LOW",
        description=f"Device '{device_name}' registered",
    ))
    db.session.commit()
    # --- Broadcast to dashboard ---
    from app.websocket.events import broadcast_event
    broadcast_event("device_registered", device.to_dict())
    return jsonify({
        "success": True,
        "data": {
            "device_id": device.device_id,
            "device_token": token,
        },
    }), 201
# ---------- Heartbeat ----------
@client_bp.route("/api/client/heartbeat", methods=["POST"])
def heartbeat():
    """Update last_active_time, set status=ONLINE, store metrics, evaluate alerts."""
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
    db.session.flush()
    # --- Threshold alerting ---
    from app.services.alert_service import evaluate_alerts
    alert_count = evaluate_alerts(device.device_id, data)
    if alert_count:
        print(f"[alert] {alert_count} alert(s) for device {device.device_id}")
    db.session.commit()
    # --- Broadcast to dashboard ---
    from app.websocket.events import broadcast_event
    broadcast_event("device_heartbeat", {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "status": device.status,
        "last_active_time": device.last_active_time.isoformat() if device.last_active_time else None,
        "metrics": data,
    })
    if was_offline:
        broadcast_event("device_status_change", {
            "device_id": device.device_id,
            "status": "ONLINE",
            "device_name": device.device_name,
        })
    if alert_count:
        broadcast_event("new_alert", {
            "device_id": device.device_id,
            "count": alert_count,
        })
    return jsonify({
        "success": True,
        "data": {
            "device_id": device.device_id,
            "status": device.status,
            "server_time": datetime.utcnow().isoformat(),
        },
    }), 200


    # ---------- Session polling (agent side) ----------

@client_bp.route("/api/client/pending-session", methods=["GET"])
def pending_session():
    """Agent polls this to see if an admin requested a remote session."""
    device = _device_from_request()
    if device is None:
        return jsonify({"success": False, "message": "Invalid or missing device token"}), 401

    from app.services.session_service import list_pending_for_device
    sess = list_pending_for_device(device.device_id)
    if sess is None:
        return jsonify({"success": True, "data": None}), 200

    return jsonify({
        "success": True,
        "data": {
            "session_id": sess.session_id,
            "session_type": sess.session_type,
            "connection_status": sess.connection_status,
            "start_time": sess.start_time.isoformat() if sess.start_time else None,
        },
    }), 200


@client_bp.route("/api/client/session-status", methods=["POST"])
def session_status():
    """Agent reports a session status change."""
    device = _device_from_request()
    if device is None:
        return jsonify({"success": False, "message": "Invalid or missing device token"}), 401

    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    status = (data.get("status") or "").upper()

    if not session_id or status not in ("CONNECTED", "DISCONNECTED", "FAILED"):
        return jsonify({"success": False, "message": "session_id and valid status required"}), 400

    from app.services.session_service import get_session, update_session_status
    sess = get_session(session_id)
    if sess is None or sess.device_id != device.device_id:
        return jsonify({"success": False, "message": "Session not found for this device"}), 404

    update_session_status(session_id, status)

    from app.websocket.events import broadcast_event
    broadcast_event("session_update", {
        "session_id": session_id,
        "device_id": device.device_id,
        "connection_status": status,
        "session_type": sess.session_type,
    })

    return jsonify({"success": True, "data": {"session_id": session_id, "status": status}}), 200
