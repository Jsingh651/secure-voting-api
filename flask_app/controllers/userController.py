import re

from flask import jsonify, request

from flask_app import app, bcrypt, limiter
from flask_app.auth import generate_token, token_required
from flask_app.models.user import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.post("/api/register")
@limiter.limit("10 per minute")
def register():
    data = request.get_json(silent=True) or {}
    first = (data.get("first_name") or "").strip()
    last = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not (first and last and email and password):
        return jsonify({"error": "first_name, last_name, email and password are required"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email address"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if User.by_email(email):
        return jsonify({"error": "Email is already registered"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User.create(first, last, email, password_hash)
    if not user:
        return jsonify({"error": "Could not create account"}), 500

    token = generate_token(user["id"], user["role"])
    return jsonify({"token": token, "user_id": user["id"]}), 201


@app.post("/api/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.by_email(email)
    if not user or not bcrypt.check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["id"], user["role"])
    return jsonify({"token": token, "user_id": user["id"]}), 200


@app.get("/api/me")
@token_required
def me():
    user = User.by_id(request.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200
