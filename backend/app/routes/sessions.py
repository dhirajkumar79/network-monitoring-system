from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services import session_service
from app.utils.decorators import role_required

sessions_bp = Blueprint("sessions_bp", __name__)


@sessions_bp.route("/api/sessions", methods=["GET"])
@jwt_required()
def list_sessions():
    sessions = session_service.list_sessions()
    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in sessions],
    }), 200


@sessions_bp.route("/api/sessions/<int:session_id>", methods=["GET"])
@jwt_required()
def get_session(session_id):
    sess = session_service.get_session(session_id)
    if sess is None:
        return jsonify({"success": False, "message": "Session not found"}), 404
    return jsonify({"success": True, "data": sess.to_dict()}), 200


@sessions_bp.route("/api/sessions", methods=["POST"])
@role_required("ADMIN")
def create_session():
    """Request a new session (ADMIN only)."""
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id")
    session_type = data.get("session_type", "REMOTE_DESKTOP")

    if not device_id:
        return jsonify({"success": False, "message": "device_id is required"}), 400

    if session_type != "REMOTE_DESKTOP":
        return jsonify({"success": False, "message": "Unsupported session_type"}), 400

    user_id = int(get_jwt_identity())

    result = session_service.request_remote_session(device_id, user_id)
    if "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 400

    sess = result["session"]

    from app.websocket.events import broadcast_event
    broadcast_event("session_update", {
        "session_id": sess.session_id,
        "device_id": sess.device_id,
        "connection_status": sess.connection_status,
        "session_type": sess.session_type,
    })

    return jsonify({"success": True, "data": sess.to_dict()}), 201


@sessions_bp.route("/api/sessions/<int:session_id>/end", methods=["POST"])
@role_required("ADMIN")
def end_session(session_id):
    sess = session_service.end_session(session_id)
    if sess is None:
        return jsonify({"success": False, "message": "Session not found"}), 404

    from app.websocket.events import broadcast_event
    broadcast_event("session_update", {
        "session_id": sess.session_id,
        "device_id": sess.device_id,
        "connection_status": sess.connection_status,
        "session_type": sess.session_type,
    })

    return jsonify({"success": True, "data": sess.to_dict()}), 200