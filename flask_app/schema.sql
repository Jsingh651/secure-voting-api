-- PostgreSQL schema for the VoteSmartt voting system (ported from MySQL).
-- Loaded automatically by the postgres container on first start.
-- Note: camelCase columns ("isAdmin", "created_byFK") are quoted to preserve
-- case, because the model code reads those exact dict keys.

CREATE TABLE IF NOT EXISTS users (
    user_id     SERIAL PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    phone       VARCHAR(50),
    created_at  TIMESTAMP NOT NULL DEFAULT now(),
    "isAdmin"   SMALLINT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS event (
    event_id       SERIAL PRIMARY KEY,
    title          VARCHAR(150) NOT NULL,
    description    VARCHAR(255),
    start_time     TIMESTAMP,
    end_time       TIMESTAMP,
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    "created_byFK" INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    status         VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS "option" (
    option_id        SERIAL PRIMARY KEY,
    option_text      VARCHAR(255) NOT NULL,
    option_event_id  INTEGER NOT NULL REFERENCES event(event_id) ON DELETE CASCADE,
    created_at       TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS vote (
    vote_id        SERIAL PRIMARY KEY,
    voted_at       TIMESTAMP NOT NULL DEFAULT now(),
    vote_user_id   INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    vote_option_id INTEGER NOT NULL REFERENCES "option"(option_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS password_reset_token (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash  VARCHAR(128) NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    used_at     TIMESTAMP NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_option_event ON "option"(option_event_id);
CREATE INDEX IF NOT EXISTS idx_vote_option  ON vote(vote_option_id);
CREATE INDEX IF NOT EXISTS idx_vote_user    ON vote(vote_user_id);
CREATE INDEX IF NOT EXISTS idx_prt_hash     ON password_reset_token(token_hash);
