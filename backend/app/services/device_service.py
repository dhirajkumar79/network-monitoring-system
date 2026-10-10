from datetime import datetime, timedelta
from app.extensions import db
from app.models.device import Device
from app.models.event import Event
def list_devices(status: str = None):
    """Return all devices, optionally filtered by status."""
    query = Device.query
    if status:
        query = query.filter_by(status=status.upper())
    return query.order_by(Device.device_id.asc()).all()
def get_device(device_id: int):
    return db.session.get(Device, device_id)
def get_device_metrics(device_id: int, limit: int = 50):
    """Return recent metrics for a device, newest first."""
    from app.models.metric import NetworkMetric
    return (
        NetworkMetric.query
        .filter_by(device_id=device_id)
        .order_by(NetworkMetric.timestamp.desc())
        .limit(limit)
        .all()
    )
def get_device_events(device_id: int, limit: int = 50):
    return (
        Event.query
        .filter_by(device_id=device_id)
        .order_by(Event.timestamp.desc())
        .limit(limit)
        .all()
    )
def mark_stale_devices_offline(timeout_seconds: int) -> int:
    """Mark devices OFFLINE whose last_active_time is older than the timeout.
    Creates a DEVICE_OFFLINE event for each device that transitions.
    Broadcasts via Socket.IO to the dashboard.
    Returns the number of devices marked offline.
    """
    threshold = datetime.utcnow() - timedelta(seconds=timeout_seconds)
    stale = (
        Device.query
        .filter(Device.status == "ONLINE")
        .filter(
            (Device.last_active_time == None)  # noqa: E711
            | (Device.last_active_time < threshold)
        )
        .all()
    )
    count = 0
    for device in stale:
        device.status = "OFFLINE"
        db.session.add(Event(
            device_id=device.device_id,
            event_type="DEVICE_OFFLINE",
            severity="MEDIUM",
            description=f"Device '{device.device_name}' stopped responding",
        ))
        count += 1
    if count:
        db.session.commit()
        # --- Broadcast to dashboard ---
        try:
            from app.websocket.events import broadcast_event
            for device in stale:
                broadcast_event("device_status_change", {
                    "device_id": device.device_id,
                    "status": "OFFLINE",
                    "device_name": device.device_name,
                })
        except Exception as exc:
            print(f"[socketio] Offline broadcast failed: {exc}")
    return count

def delete_device(device_id: int) -> bool:
    """Delete a device and all its related data (metrics, events, sessions).

    Returns True if the device existed and was deleted, False otherwise.
    """
    from app.models.metric import NetworkMetric
    from app.models.session import Session

    device = db.session.get(Device, device_id)
    if device is None:
        return False

    # Delete child rows first (foreign key order)
    NetworkMetric.query.filter_by(device_id=device_id).delete()
    Event.query.filter_by(device_id=device_id).delete()
    Session.query.filter_by(device_id=device_id).delete()

    # Delete the device itself
    db.session.delete(device)
    db.session.commit()
    return True
