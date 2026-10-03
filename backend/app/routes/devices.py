from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services import device_service

devices_bp = Blueprint("devices_bp", __name__)


@devices_bp.route("/api/devices", methods=["GET"])
@jwt_required()
def list_devices():
    """GET /api/devices?status=ONLINE
    Returns all devices, optionally filtered by status.
    """
    status = request.args.get("status")
    devices = device_service.list_devices(status=status)
    return jsonify({
        "success": True,
        "data": [d.to_dict() for d in devices],
    }), 200


@devices_bp.route("/api/devices/<int:device_id>", methods=["GET"])
@jwt_required()
def get_device(device_id):
    device = device_service.get_device(device_id)
    if device is None:
        return jsonify({"success": False, "message": "Device not found"}), 404
    return jsonify({"success": True, "data": device.to_dict()}), 200


@devices_bp.route("/api/devices/<int:device_id>/metrics", methods=["GET"])
@jwt_required()
def get_device_metrics(device_id):
    device = device_service.get_device(device_id)
    if device is None:
        return jsonify({"success": False, "message": "Device not found"}), 404

    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 500))

    metrics = device_service.get_device_metrics(device_id, limit=limit)
    return jsonify({
        "success": True,
        "data": [m.to_dict() for m in metrics],
    }), 200


@devices_bp.route("/api/devices/<int:device_id>/events", methods=["GET"])
@jwt_required()
def get_device_events(device_id):
    device = device_service.get_device(device_id)
    if device is None:
        return jsonify({"success": False, "message": "Device not found"}), 404

    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 500))

    events = device_service.get_device_events(device_id, limit=limit)
    return jsonify({
        "success": True,
        "data": [e.to_dict() for e in events],
    }), 200