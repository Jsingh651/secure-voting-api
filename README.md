# Project Golf: Electronic Voting System

A full-stack electronic voting platform: users register, administrators create
elections with candidates, voters cast and change ballots while voting is open,
and results are published once an election closes.

Built with Flask + **PostgreSQL**, secured with **token-based auth (JWT)** and
**rate limiting**, **containerized with Docker**, and deployed to **AWS EC2**.

## Features
- **Auth:** registration/login with bcrypt-hashed passwords, session-based UI
  plus a JWT bearer-token API (`/api/login`, `/api/me`); role-based access
  (voter vs admin); secure, expiring password-reset tokens.
- **Elections:** admins create timed events with 2+ candidates; status
  (Waiting / Open / Closed) is computed from start/end times.
- **Voting integrity:** one ballot per voter per election; ballots can be
  changed or retracted while voting is open; results locked until close.
- **Results:** live tallies, percentages, and winner/tie detection.
- **Rate limiting** on auth endpoints (Flask-Limiter) to resist abuse.
- **Dashboards:** voter profile + voting history; admin user management.

## Tech stack
- **Backend:** Python 3.12, Flask, gunicorn
- **Database:** PostgreSQL (psycopg2, threaded connection pool)
- **Auth:** PyJWT, Flask-Bcrypt
- **Infra:** Docker, docker-compose, AWS EC2, GitHub Actions

## Run it locally
```bash
cp .env.example .env          # set SECRET_KEY, JWT_SECRET, DB_PASSWORD
docker compose up --build
```
App: http://localhost:8000 — the Postgres schema (`flask_app/schema.sql`) is
applied automatically on first start.

## Configuration
All config is via environment variables (see `.env.example`); no secrets live
in the codebase. Generate strong secrets with:
`python -c "import secrets; print(secrets.token_hex(32))"`
