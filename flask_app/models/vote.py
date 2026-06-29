from flask_app.db import query_db


class Vote:
    @classmethod
    def cast(cls, election_id, candidate_id, user_id):
        """Record a vote, or update it if the user already voted in this election.

        The ON CONFLICT clause relies on the UNIQUE (election_id, user_id)
        constraint to guarantee one ballot per voter per election.
        """
        query_db(
            """
            INSERT INTO votes (election_id, candidate_id, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (election_id, user_id)
            DO UPDATE SET candidate_id = EXCLUDED.candidate_id, updated_at = now()
            """,
            (election_id, candidate_id, user_id),
        )
