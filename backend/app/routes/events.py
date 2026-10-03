from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.event import Event

events_bp = Blueprint("events_bp", __name__)


@events_bp.route("/api/events", methods=["GET"])
@jwt_required()
def list_events():
    """GET /api/events?severity=HIGH&event_type=DEVICE_ONLINE&device_id=1&limit=100
    Returns events with optional filtering.
    """
    query = Event.query

    severity = request.args.get("severity")
    if severity:
        query = query.filter_by(severity=severity.upper())

    event_type = request.args.get("event_type")
    if event_type:
        query = query.filter_by(event_type=event_type.upper())

    device_id = request.args.get("device_id", type=int)
    if device_id:
        query = query.filter_by(device_id=device_id)

    since = request.args.get("since")
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.filter(Event.timestamp >= since_dt)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid 'since' format"}), 400

    limit = request.args.get("limit", default=100, type=int)
    limit = max(1, min(limit, 1000))

    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    return jsonify({
        "success": True,
        "data": [e.to_dict() for e in events],
    }), 200