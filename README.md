# Project Golf – Electronic Voting System

A secure electronic voting service built with **Flask (Python)** and
**PostgreSQL**. It provides token-based authentication, rate limiting, a
normalized relational schema that guarantees one ballot per voter per election,
and a containerized deployment pipeline to AWS EC2 via GitHub Actions.

> Originally a CSC-131 team project (Fall 2025).

## Features

- **Token-based auth (JWT):** register/login, bcrypt-hashed passwords, signed
  bearer tokens, role-based access (`voter` / `admin`).
- **Rate limiting:** per-client limits (Flask-Limiter) on auth and voting
  endpoints to protect against abuse.
- **Vote integrity:** a `UNIQUE (election_id, user_id)` constraint plus an
  upsert means each voter has exactly one ballot per election and can change
  it until the deadline.
- **Connection pooling:** a threaded PostgreSQL pool keeps latency low under
  concurrent load.
- **Containerized & CI/CD:** Docker + docker-compose, with GitHub Actions
  running tests and a Docker build on every push and deploying to EC2 on `main`.
- **Load test included:** a Locust scenario to measure real throughput/latency.

## Tech stack

- Backend: Python 3.12, Flask, gunicorn
- Database: PostgreSQL (`psycopg2`, connection pooling) — runs as a Docker container alongside the app
- Auth: PyJWT, Flask-Bcrypt
- Infra: Docker, docker-compose, GitHub Actions, AWS EC2
- Testing/Load: pytest, Locust

## Project structure

```
flask_app/
  __init__.py            # app, bcrypt, rate limiter; registers controllers
  db.py                  # PostgreSQL connection pool + query helper
  auth.py                # JWT generation/verification + auth decorators
  schema.sql             # normalized schema (users, elections, candidates, votes)
  models/                # data-access classes (User, Election, Vote)
  controllers/           # route handlers (pages, users, elections, votes)
  static/ , templates/   # frontend assets
server.py                # local dev entry point (gunicorn serves it in Docker)
Dockerfile , docker-compose.yml
locustfile.py            # load test
tests/                   # pytest unit tests (no DB required)
.github/workflows/       # CI/CD pipeline
DEPLOY.md                # step-by-step AWS deployment guide
```

## Quick start (Docker — recommended)

```bash
cp .env.example .env        # set SECRET_KEY and JWT_SECRET
docker compose up --build
```

App runs at http://localhost:8000 (health check at `/healthz`). The schema is
applied automatically on first start.

## Quick start (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# point these at a running PostgreSQL instance
export DB_HOST=localhost DB_USER=voting DB_PASSWORD=votingpass DB_NAME=votingdb
export SECRET_KEY=dev JWT_SECRET=dev
psql "$DB_NAME" < flask_app/schema.sql      # create tables

python server.py        # http://localhost:8000
```

## API overview

| Method & path | Auth | Purpose |
|---|---|---|
| `POST /api/register` | — | Create account, returns a JWT |
| `POST /api/login` | — | Log in, returns a JWT |
| `GET  /api/me` | Bearer | Current user profile |
| `POST /api/elections` | Admin | Create an election + candidates |
| `GET  /api/elections` | Bearer | List elections |
| `POST /api/elections/<id>/vote` | Bearer | Cast / change your vote |
| `GET  /api/elections/<id>/results` | Bearer | Results (after close) |
| `GET  /healthz` | — | Liveness probe |

Send the token as `Authorization: Bearer <token>`.

## Configuration

All configuration is via environment variables — see `.env.example`. **No
secrets are stored in the codebase.** Generate strong secrets with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Deployment

See [DEPLOY.md](DEPLOY.md) for the full Docker → AWS EC2 → GitHub Actions guide,
including how to measure real performance numbers with the included load test.

## Team

| Name | Role |
|------|------|
| Jang Singh & Derek | Project Manager & Documentation Lead |
| Ceaser | Analyst |
| Darren & Arav | Designer |
| Yucheng Yu & Ceaser | Frontend Developer |
| Alex & Darren | Backend Developer |
| Derek | Database Engineer |
| Jarret | QA / Test Engineer |
