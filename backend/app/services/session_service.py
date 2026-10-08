"""Session management: monitoring and remote-desktop sessions."""

from datetime import datetime
from typing import Optional

from app.extensions import db
from app.models.device import Device
from app.models.event import Event
from app.models.session import Session


def list_sessions(limit: int = 100):
    return (
        Session.query
        .order_by(Session.start_time.desc())
        .limit(limit)
        .all()
    )


def get_session(session_id: int) -> Optional[Session]:
    return db.session.get(Session, session_id)


def list_pending_for_device(device_id: int) -> Optional[Session]:
    """Return the oldest CONNECTING session for this device, if any."""
    return (
        Session.query
        .filter_by(device_id=device_id, connection_status="CONNECTING")
        .order_by(Session.start_time.asc())
        .first()
    )


def request_remote_session(device_id: int, user_id: int) -> dict:
    """Create a REMOTE_DESKTOP session request."""
    device = db.session.get(Device, device_id)
    if device is None:
        return {"error": "Device not found"}

    if device.status != "ONLINE":
        return {"error": "Device is not online"}

    existing = list_pending_for_device(device_id)
    if existing is not None:
        return {"error": "A session is already pending for this device"}

    sess = Session(
        device_id=device_id,
        user_id=user_id,
        start_time=datetime.utcnow(),
        connection_status="CONNECTING",
        session_type="REMOTE_DESKTOP",
    )
    db.session.add(sess)
    db.session.flush()

    db.session.add(Event(
        device_id=device_id,
        event_type="REMOTE_SESSION_REQUESTED",
        severity="MEDIUM",
        description=f"Remote session requested by user_id={user_id}",
    ))
    db.session.commit()

    return {"session": sess}


def update_session_status(session_id: int, new_status: str) -> Optional[Session]:
    """Called by the agent to report CONNECTED / FAILED / DISCONNECTED."""
    sess = db.session.get(Session, session_id)
    if sess is None:
        return None

    sess.connection_status = new_status

    if new_status in ("DISCONNECTED", "FAILED"):
        sess.end_time = datetime.utcnow()

    event_map = {
        "CONNECTED": ("REMOTE_SESSION_STARTED", "LOW"),
        "DISCONNECTED": ("REMOTE_SESSION_ENDED", "LOW"),
        "FAILED": ("REMOTE_SESSION_FAILED", "MEDIUM"),
    }
    if new_status in event_map:
        event_type, severity = event_map[new_status]
        db.session.add(Event(
            device_id=sess.device_id,
            event_type=event_type,
            severity=severity,
            description=f"Session {session_id} {new_status.lower()}",
        ))

    db.session.commit()
    return sess


def end_session(session_id: int) -> Optional[Session]:
    """Admin-initiated end."""
    return update_session_status(session_id, "DISCONNECTED")