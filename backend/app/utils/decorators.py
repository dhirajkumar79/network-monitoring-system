from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def role_required(*allowed_roles):
    """Decorator: only allow users whose JWT role is in allowed_roles.

    Skips JWT check on OPTIONS requests so CORS preflight succeeds.

    Usage:
        @role_required("ADMIN")
        def some_view(): ...
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            # Let CORS preflight (OPTIONS) pass through without auth check
            if request.method == "OPTIONS":
                return jsonify({"success": True}), 200

            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return (
                    jsonify({"success": False, "message": "Forbidden: insufficient role"}),
                    403,
                )
            return fn(*args, **kwargs)
        return decorated
    return wrapper