from flask import jsonify, request

from flask_app import app, limiter
from flask_app.auth import token_required
from flask_app.models.election import Election
from flask_app.models.vote import Vote


@app.post("/api/elections/<int:election_id>/vote")
@limiter.limit("30 per minute")
@token_required
def cast_vote(election_id):
    data = request.get_json(silent=True) or {}
    candidate_id = data.get("candidate_id")
    if not candidate_id:
        return jsonify({"error": "candidate_id is required"}), 400

    status = Election.status(election_id)
    if not status:
        return jsonify({"error": "Election not found"}), 404
    if not status["is_open"]:
        return jsonify({"error": "Election is not open for voting"}), 403
    if not Election.has_candidate(election_id, candidate_id):
        return jsonify({"error": "Invalid candidate for this election"}), 400

    Vote.cast(election_id, candidate_id, request.user_id)
    return jsonify({"status": "vote recorded"}), 200
