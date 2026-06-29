from flask_app.db import query_db


class User:
    @classmethod
    def create(cls, first_name, last_name, email, password_hash):
        rows = query_db(
            """
            INSERT INTO users (first_name, last_name, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id, role
            """,
            (first_name, last_name, email, password_hash),
        )
        return rows[0] if rows else None

    @classmethod
    def by_email(cls, email):
        rows = query_db("SELECT * FROM users WHERE email = %s", (email,))
        return rows[0] if rows else None

    @classmethod
    def by_id(cls, user_id):
        rows = query_db(
            """
            SELECT id, first_name, last_name, email, role, created_at
            FROM users WHERE id = %s
            """,
            (user_id,),
        )
        return rows[0] if rows else None
