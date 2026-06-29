"""PostgreSQL access layer.

Uses a threaded connection pool so the app can serve many concurrent voters
without paying the cost of opening a fresh TCP/TLS connection per request.
All queries flow through ``query_db`` which manages transactions for you.
"""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

_pool = None


def _build_pool():
    return psycopg2.pool.ThreadedConnectionPool(
        minconn=int(os.environ.get("DB_POOL_MIN", 1)),
        maxconn=int(os.environ.get("DB_POOL_MAX", 20)),
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 5432)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ.get("DB_NAME", "votingdb"),
        sslmode=os.environ.get("DB_SSLMODE", "prefer"),
    )


def get_pool():
    """Lazily create the pool on first use (keeps imports DB-free for tests)."""
    global _pool
    if _pool is None:
        _pool = _build_pool()
    return _pool


@contextmanager
def get_conn():
    p = get_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def query_db(query, data=None):
    """Run a query and return rows for SELECT / RETURNING, else the row count.

    Returns ``False`` on error so callers can fail safe.
    """
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, data)
                if cur.description:  # SELECT, or INSERT/UPDATE ... RETURNING
                    return cur.fetchall()
                return cur.rowcount
    except Exception as e:  # pragma: no cover - defensive logging
        print("Database error:", e)
        return False
