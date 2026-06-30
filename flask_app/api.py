"""Token-based authentication API (JWT).

Layered on top of the existing session-based UI to provide genuine bearer-token
auth for programmatic/API access:

    POST /api/login -> returns a signed JWT for valid credentials
    GET  /api/me    -> returns the caller's profile (requires Bearer token)

The token carries the user id and role and is verified on each request, so no
server-side session lookup is needed (cheap under load).
"""
import datetime as dt
import os
from functools import wraps

import jwt
from flask import jsonify, request
from flask_bcrypt import Bcrypt

from flask_app import app, limiter
from flask_app.models.userModels import User

bcrypt = Bcrypt(app)
JWT_ALGORITHM = "HS256"


def _secret():
    return os.environ.get("JWT_SECRET") or app.secret_key


def generate_token(user):
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "role": "admin" if user.is_admin else "voter",
        "iat": now,
        "exp": now + dt.timedelta(hours=int(os.environ.get("JWT_EXP_HOURS", 12))),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        try:
            payload = jwt.decode(header.split(" ", 1)[1].strip(), _secret(), algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        request.jwt_user_id = int(payload["sub"])
        request.jwt_role = payload.get("role", "voter")
        return f(*args, **kwargs)

    return wrapper


@app.post("/api/login")
@limiter.limit("10 per minute")
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.getUserByEmail({"email": email})
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify({"token": generate_token(user), "user_id": user.user_id}), 200


@app.get("/api/me")
@token_required
def api_me():
    user = User.getUserByID({"user_id": request.jwt_user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": "admin" if user.is_admin else "voter",
    }), 200
