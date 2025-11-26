from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def role_required(allowed_roles: list):
    """
    Decorator to restrict access based on user role.
    Example: @role_required(["admin"])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Validate JWT
            verify_jwt_in_request()

            # Extract identity payload
            identity = get_jwt_identity()  # Expected: {"id": user_id, "role": "admin"}

            # Safety check
            user_role = identity.get("role") if isinstance(identity, dict) else None

            if user_role not in allowed_roles:
                return jsonify({"msg": "Forbidden: Insufficient role permissions"}), 403

            # Proceed with the endpoint
            return fn(*args, **kwargs)

        return wrapper
    return decorator
