"""Load test for the voting service.

This is how you *honestly* substantiate throughput/latency numbers: run it
against a real deployment and read the numbers Locust reports.

Example — simulate 4,000 concurrent voters, ramping 200/sec:

    pip install -r requirements-dev.txt
    locust -f locustfile.py --host http://YOUR_SERVER:8000 \
           --users 4000 --spawn-rate 200

Then open http://localhost:8089 and watch the median/95th percentile latency.
For the vote task to succeed, election id 1 with candidate id 1 must exist.
"""
import random

from locust import HttpUser, between, task


class VoterUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        email = f"load_{random.randint(0, 10_000_000)}@example.com"
        resp = self.client.post(
            "/api/register",
            json={
                "first_name": "Load",
                "last_name": "Test",
                "email": email,
                "password": "password123",
            },
            name="/api/register",
        )
        self.token = resp.json().get("token") if resp.ok else None

    @task(3)
    def vote(self):
        if not self.token:
            return
        self.client.post(
            "/api/elections/1/vote",
            json={"candidate_id": 1},
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/elections/[id]/vote",
        )

    @task(1)
    def list_elections(self):
        if not self.token:
            return
        self.client.get(
            "/api/elections",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/api/elections",
        )
