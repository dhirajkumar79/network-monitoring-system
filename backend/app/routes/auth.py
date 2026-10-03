from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)

from app.services.auth_service import authenticate, get_user_by_id

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    user = authenticate(username, password)
    if user is None:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # Identity must be a string in newer flask-jwt-extended
    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={"role": user.role, "username": user.username},
    )

    return jsonify({
        "success": True,
        "data": {
            "access_token": access_token,
            "user": user.to_dict(),
        },
    }), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = get_user_by_id(int(user_id))
    if user is None:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "data": user.to_dict()}), 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    # With stateless JWTs, "logout" is done client-side by discarding the token.
    # We return 200 to acknowledge. (A token-blocklist can be added later.)
    return jsonify({"success": True, "data": {"message": "Logged out"}}), 200