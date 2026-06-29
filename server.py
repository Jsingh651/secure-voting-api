import os

from flask_app import app

if __name__ == "__main__":
    # Local development entry point. In production the app is served by gunicorn
    # (see the Dockerfile CMD), which imports `app` from this module directly.
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
