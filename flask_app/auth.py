"""Token-based authentication using JSON Web Tokens (JWT).

Clients log in once, receive a signed token, and present it as
``Authorization: Bearer <token>`` on every protected request. The token is
self-contained (carries the user id + role) so no server-side session lookup
is needed, which keeps auth cheap under load.
"""
import datetime as dt
import os
from functools import wraps

import jwt
from flask import jsonify, request

JWT_ALGORITHM = "HS256"


def _secret():
    return os.environ.get("JWT_SECRET") or os.environ.get("SECRET_KEY", "dev-only-change-me")


def generate_token(user_id, role):
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + dt.timedelta(hours=int(os.environ.get("JWT_EXP_HOURS", 12))),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def decode_token(token):
    return jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.split(" ", 1)[1].strip()
    return None


def token_required(f):
    """Reject requests without a valid token; attach user id/role to request."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        request.user_id = int(payload["sub"])
        request.user_role = payload.get("role", "voter")
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    """Like ``token_required`` but also enforces the admin role."""

    @wraps(f)
    @token_required
    def wrapper(*args, **kwargs):
        if getattr(request, "user_role", None) != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)

    return wrapper
