from flask import jsonify, request

from flask_app import app
from flask_app.auth import admin_required, token_required
from flask_app.models.election import Election


@app.post("/api/elections")
@admin_required
def create_election():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    opens_at = data.get("opens_at")
    closes_at = data.get("closes_at")
    candidates = data.get("candidates") or []

    if not (title and opens_at and closes_at):
        return jsonify({"error": "title, opens_at and closes_at are required"}), 400
    if len(candidates) < 2:
        return jsonify({"error": "At least two candidates are required"}), 400

    election_id = Election.create(
        title, data.get("description"), request.user_id, opens_at, closes_at
    )
    if not election_id:
        return jsonify({"error": "Could not create election"}), 500

    for candidate in candidates:
        name = (candidate.get("name") or "").strip()
        if name:
            Election.add_candidate(election_id, name, candidate.get("description"))

    return jsonify({"election_id": election_id}), 201


@app.get("/api/elections")
@token_required
def list_elections():
    return jsonify(Election.all()), 200


@app.get("/api/elections/<int:election_id>/results")
@token_required
def election_results(election_id):
    status = Election.status(election_id)
    if not status:
        return jsonify({"error": "Election not found"}), 404
    if not status["is_closed"]:
        return jsonify({"error": "Results are available after voting closes"}), 403

    return jsonify({"election_id": election_id, "results": Election.results(election_id)}), 200
