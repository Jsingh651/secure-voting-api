"""Unit tests that do not require a live database.

They exercise the auth/token layer and the access-control guards, which run
before any DB access, so CI can validate the app without a Postgres instance.
"""
import os

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret")

from flask_app import app  # noqa: E402
from flask_app.auth import decode_token, generate_token  # noqa: E402


def test_token_roundtrip():
    token = generate_token(42, "admin")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_me_requires_token():
    client = app.test_client()
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_admin_route_rejects_voter_token():
    client = app.test_client()
    token = generate_token(1, "voter")
    resp = client.post(
        "/api/elections",
        json={"title": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_healthz():
    client = app.test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
