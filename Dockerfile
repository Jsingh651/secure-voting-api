FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user up front so copied files can be owned by it.
RUN useradd --create-home appuser

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app owned by appuser (host file modes may not be world-readable).
COPY --chown=appuser:appuser . .

EXPOSE 8000

USER appuser

# 4 worker processes x 2 threads handles many concurrent voters per instance.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", \
     "--timeout", "30", "--access-logfile", "-", "server:app"]
