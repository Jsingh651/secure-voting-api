# Deployment Guide — Docker → AWS EC2 via GitHub Actions

This walks you from "no AWS account" to "app running on EC2 and auto-deploying
on every push to `main`". You run these steps; nothing here is automated for you.

---

## 0. Rotate the leaked database credentials first

The old Aiven MySQL password was committed to a public repo, so treat it as
compromised. Either delete that Aiven service or reset its password before
doing anything else. This project now uses PostgreSQL and reads all secrets
from environment variables — no credentials live in the code.

---

## 1. Run it locally with Docker (verify before deploying)

```bash
cp .env.example .env          # then edit SECRET_KEY / JWT_SECRET
docker compose up --build
```

- App: http://localhost:8000  (health check: http://localhost:8000/healthz)
- The Postgres schema in `flask_app/schema.sql` is applied automatically.

Smoke test the API:

```bash
curl -X POST localhost:8000/api/register \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"A","last_name":"B","email":"a@b.com","password":"password123"}'
```

You should get back a JSON token.

---

## 2. Create an AWS account & launch an EC2 instance

1. Sign up at https://aws.amazon.com (free tier covers a small instance).
2. Console → **EC2** → **Launch instance**:
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Type:** `t3.small` (t2.micro works for a demo but is tight)
   - **Key pair:** create one, download the `.pem`, keep it safe
   - **Security group** — allow inbound:
     - SSH (22) from **My IP**
     - Custom TCP (8000) from **Anywhere** (or 80 if you add a reverse proxy)
3. Launch, then note the instance's **Public IPv4 address**.

---

## 3. Install Docker on the instance

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# on the instance:
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu
exit            # log out/in so the docker group applies
```

---

## 4. Clone, configure, and run

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
git clone https://github.com/Jsingh651/secure-voting-api.git
cd secure-voting-api
cp .env.example .env
nano .env
```

The database runs as a Postgres container on this same instance, so you only
need to set three values in `.env` (generate the secrets with
`python3 -c "import secrets; print(secrets.token_hex(32))"`):

```
SECRET_KEY=<a long random string>
JWT_SECRET=<a different long random string>
DB_PASSWORD=<a strong password for the postgres container>
```

Start the stack (app + its own Postgres; the schema is applied automatically):

```bash
docker compose up -d --build
curl localhost:8000/healthz     # -> {"status":"ok"}
```

Your app is now at `http://YOUR_EC2_IP:8000`.

> **Backups (optional).** Data lives in the `pgdata` Docker volume on this
> instance. For a nightly dump, add a cron entry with `crontab -e`:
> ```
> 0 3 * * * cd ~/secure-voting-api && docker compose exec -T db pg_dump -U voting votingdb | gzip > ~/backup-$(date +\%F).sql.gz
> ```

---

## 5. Wire up GitHub Actions auto-deploy

The workflow (`.github/workflows/ci-deploy.yml`) runs tests + a Docker build on
every push/PR, and deploys to EC2 on push to `main` — but only once you opt in.

In your GitHub repo → **Settings**:

- **Secrets and variables → Actions → Secrets**, add:
  - `EC2_HOST` = your EC2 public IP
  - `EC2_USER` = `ubuntu`
  - `EC2_SSH_KEY` = the full contents of your `.pem` private key
- **Secrets and variables → Actions → Variables**, add:
  - `DEPLOY_ENABLED` = `true`

Now every push to `main` SSHes in, pulls, and restarts the containers.

---

## 6. Substantiate the performance claims (honestly)

To back "N concurrent voters at < 200 ms", actually measure it:

```bash
pip install -r requirements-dev.txt
locust -f locustfile.py --host http://YOUR_EC2_IP:8000 --users 4000 --spawn-rate 200
```

Open http://localhost:8089 and record the real median / 95th-percentile latency
and failure rate. Use **those** numbers — scale the instance size and gunicorn
worker count until they hold, then quote what you measured.

---

## Notes / next steps

- For real uptime numbers, put the instance behind an uptime monitor
  (e.g. UptimeRobot hitting `/healthz`) and report what it records over time.
- For production-grade rate limiting across workers, run Redis and set
  `RATELIMIT_STORAGE_URI=redis://...`.
- Consider an Application Load Balancer + HTTPS (ACM certificate) before
  exposing this to real users.
