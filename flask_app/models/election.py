from flask_app.db import query_db


class Election:
    @classmethod
    def create(cls, title, description, created_by, opens_at, closes_at):
        rows = query_db(
            """
            INSERT INTO elections (title, description, created_by, opens_at, closes_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (title, description, created_by, opens_at, closes_at),
        )
        return rows[0]["id"] if rows else None

    @classmethod
    def add_candidate(cls, election_id, name, description):
        query_db(
            "INSERT INTO candidates (election_id, name, description) VALUES (%s, %s, %s)",
            (election_id, name, description),
        )

    @classmethod
    def all(cls):
        return query_db(
            """
            SELECT id, title, description, opens_at, closes_at
            FROM elections
            ORDER BY opens_at DESC
            """
        ) or []

    @classmethod
    def status(cls, election_id):
        """Return open/closed flags for an election, or None if it doesn't exist."""
        rows = query_db(
            """
            SELECT (now() BETWEEN opens_at AND closes_at) AS is_open,
                   (now() >= closes_at)                   AS is_closed
            FROM elections WHERE id = %s
            """,
            (election_id,),
        )
        return rows[0] if rows else None

    @classmethod
    def has_candidate(cls, election_id, candidate_id):
        rows = query_db(
            "SELECT id FROM candidates WHERE id = %s AND election_id = %s",
            (candidate_id, election_id),
        )
        return bool(rows)

    @classmethod
    def results(cls, election_id):
        return query_db(
            """
            SELECT c.id AS candidate_id, c.name, COUNT(v.id) AS votes
            FROM candidates c
            LEFT JOIN votes v ON v.candidate_id = c.id
            WHERE c.election_id = %s
            GROUP BY c.id, c.name
            ORDER BY votes DESC, c.name ASC
            """,
            (election_id,),
        ) or []
