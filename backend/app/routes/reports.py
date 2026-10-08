"""Aggregated reporting endpoints."""

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.device import Device
from app.models.event import Event
from app.models.metric import NetworkMetric
from app.models.session import Session

reports_bp = Blueprint("reports_bp", __name__)


def _parse_range():
    """Return (from_dt, to_dt) from query params, defaulting to last 7 days."""
    now = datetime.utcnow()
    to_str = request.args.get("to")
    from_str = request.args.get("from")

    to_dt = now
    if to_str:
        try:
            to_dt = datetime.fromisoformat(to_str)
        except ValueError:
            pass

    from_dt = to_dt - timedelta(days=7)
    if from_str:
        try:
            from_dt = datetime.fromisoformat(from_str)
        except ValueError:
            pass

    return from_dt, to_dt


@reports_bp.route("/api/reports/summary", methods=["GET"])
@jwt_required()
def summary():
    """Return counts and aggregate stats for the given date range."""
    from_dt, to_dt = _parse_range()

    total_devices = Device.query.count()
    online_now = Device.query.filter_by(status="ONLINE").count()
    offline_now = Device.query.filter_by(status="OFFLINE").count()

    events_in_range = Event.query.filter(
        Event.timestamp >= from_dt, Event.timestamp <= to_dt
    ).count()

    high_alerts = Event.query.filter(
        Event.timestamp >= from_dt,
        Event.timestamp <= to_dt,
        Event.severity.in_(["HIGH", "CRITICAL"]),
    ).count()

    sessions_in_range = Session.query.filter(
        Session.start_time >= from_dt, Session.start_time <= to_dt
    ).count()

    # Average metrics across all devices in range
    avg_row = db.session.query(
        db.func.avg(NetworkMetric.cpu_usage),
        db.func.avg(NetworkMetric.memory_usage),
        db.func.avg(NetworkMetric.latency_ms),
    ).filter(
        NetworkMetric.timestamp >= from_dt,
        NetworkMetric.timestamp <= to_dt,
    ).first()

    avg_cpu = round(float(avg_row[0]), 2) if avg_row and avg_row[0] is not None else 0
    avg_mem = round(float(avg_row[1]), 2) if avg_row and avg_row[1] is not None else 0
    avg_lat = round(float(avg_row[2]), 2) if avg_row and avg_row[2] is not None else 0

    return jsonify({
        "success": True,
        "data": {
            "from": from_dt.isoformat(),
            "to": to_dt.isoformat(),
            "total_devices": total_devices,
            "online_now": online_now,
            "offline_now": offline_now,
            "events_in_range": events_in_range,
            "high_alerts_in_range": high_alerts,
            "sessions_in_range": sessions_in_range,
            "avg_cpu": avg_cpu,
            "avg_memory": avg_mem,
            "avg_latency": avg_lat,
        },
    }), 200


@reports_bp.route("/api/reports/device-availability", methods=["GET"])
@jwt_required()
def device_availability():
    """Per-device metric counts and last-seen time in the range."""
    from_dt, to_dt = _parse_range()

    devices = Device.query.all()
    result = []
    for d in devices:
        metric_count = NetworkMetric.query.filter(
            NetworkMetric.device_id == d.device_id,
            NetworkMetric.timestamp >= from_dt,
            NetworkMetric.timestamp <= to_dt,
        ).count()

        avg_cpu = db.session.query(db.func.avg(NetworkMetric.cpu_usage)).filter(
            NetworkMetric.device_id == d.device_id,
            NetworkMetric.timestamp >= from_dt,
            NetworkMetric.timestamp <= to_dt,
        ).scalar()

        result.append({
            "device_id": d.device_id,
            "device_name": d.device_name,
            "hostname": d.hostname,
            "current_status": d.status,
            "last_active_time": d.last_active_time.isoformat() if d.last_active_time else None,
            "metric_points": metric_count,
            "avg_cpu": round(float(avg_cpu), 2) if avg_cpu is not None else 0,
        })

    return jsonify({"success": True, "data": result}), 200


@reports_bp.route("/api/reports/session-durations", methods=["GET"])
@jwt_required()
def session_durations():
    """Sessions with computed duration in seconds."""
    from_dt, to_dt = _parse_range()

    sessions = Session.query.filter(
        Session.start_time >= from_dt, Session.start_time <= to_dt
    ).order_by(Session.start_time.desc()).all()

    result = []
    for s in sessions:
        duration_s = None
        if s.end_time and s.start_time:
            duration_s = int((s.end_time - s.start_time).total_seconds())
        result.append({
            "session_id": s.session_id,
            "device_id": s.device_id,
            "user_id": s.user_id,
            "session_type": s.session_type,
            "connection_status": s.connection_status,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "duration_seconds": duration_s,
        })

    return jsonify({"success": True, "data": result}), 200


@reports_bp.route("/api/reports/metrics", methods=["GET"])
@jwt_required()
def metrics_report():
    """Raw metrics in the range, optionally filtered by device."""
    from_dt, to_dt = _parse_range()
    device_id = request.args.get("device_id", type=int)

    q = NetworkMetric.query.filter(
        NetworkMetric.timestamp >= from_dt,
        NetworkMetric.timestamp <= to_dt,
    )
    if device_id:
        q = q.filter(NetworkMetric.device_id == device_id)

    limit = request.args.get("limit", default=1000, type=int)
    limit = max(1, min(limit, 5000))

    metrics = q.order_by(NetworkMetric.timestamp.desc()).limit(limit).all()
    return jsonify({
        "success": True,
        "data": [m.to_dict() for m in metrics],
    }), 200