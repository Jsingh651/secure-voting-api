-- Normalized schema for the electronic voting system (PostgreSQL).
-- Loaded automatically by the postgres container on first start
-- (mounted into /docker-entrypoint-initdb.d). Safe to re-run by hand.

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'voter'
                  CHECK (role IN ('voter', 'admin')),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS elections (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(150) NOT NULL,
    description TEXT,
    created_by  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    opens_at    TIMESTAMPTZ NOT NULL,
    closes_at   TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (closes_at > opens_at)
);

CREATE TABLE IF NOT EXISTS candidates (
    id          SERIAL PRIMARY KEY,
    election_id INTEGER NOT NULL REFERENCES elections(id) ON DELETE CASCADE,
    name        VARCHAR(150) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS votes (
    id           SERIAL PRIMARY KEY,
    election_id  INTEGER NOT NULL REFERENCES elections(id)  ON DELETE CASCADE,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    user_id      INTEGER NOT NULL REFERENCES users(id)      ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- The core integrity rule: at most one vote per user per election.
    -- Re-voting before the deadline updates this row instead of inserting.
    UNIQUE (election_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_votes_election     ON votes(election_id);
CREATE INDEX IF NOT EXISTS idx_candidates_election ON candidates(election_id);
