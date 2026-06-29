import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from a local .env file when present (dev only).
load_dotenv()

app = Flask(__name__)
# Secret is read from the environment. The fallback is for local dev ONLY and
# must never be used in production (set SECRET_KEY in your environment / .env).
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

# Password hashing.
bcrypt = Bcrypt(app)

# Rate limiting. Defaults to in-memory storage; point RATELIMIT_STORAGE_URI at
# Redis (e.g. redis://redis:6379) when running multiple workers/instances so the
# limits are shared.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)

# Importing the controllers registers their routes on `app`. Kept at the bottom
# to avoid a circular import (controllers import `app`, `bcrypt`, `limiter`).
from flask_app.controllers import (  # noqa: E402,F401
    pageController,
    userController,
    electionController,
    voteController,
)
