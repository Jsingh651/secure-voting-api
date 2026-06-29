from flask import jsonify, render_template

from flask_app import app


@app.get("/")
def homepage():
    return render_template("homepage.html")


@app.get("/healthz")
def healthz():
    """Lightweight liveness probe for load balancers / uptime monitoring."""
    return jsonify({"status": "ok"}), 200
