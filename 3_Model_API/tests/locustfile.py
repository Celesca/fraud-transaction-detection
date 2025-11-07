from locust import HttpUser, task, between
import csv
import os
import random
import json
from typing import List, Dict


CSV_PATH = os.environ.get(
    "FRAUD_CSV",
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "fraud_mock.csv"),
)


def load_csv(path: str) -> List[Dict]:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file for load test not found: {path}")

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [r for r in reader]
    return rows


class PredictUser(HttpUser):
    """Locust user that sends POST /predict requests using rows from fraud_mock.csv.

    Usage examples:
      UI mode:
        locust -f locustfile.py --host=http://localhost:8000

      Headless (100 users, spawn 10/sec, run 2m):
        locust -f locustfile.py --headless -u 100 -r 10 -t 2m --host=http://localhost:8000

    You can override the CSV location with the FRAUD_CSV env var.
    """

    wait_time = between(1, 3)

    # Load the CSV once per worker process
    data: List[Dict] = []

    def on_start(self):
        if not self.data:
            try:
                self.data = load_csv(CSV_PATH)
                # shuffle once so different users don't always hit same sequence
                random.shuffle(self.data)
            except Exception as e:
                raise RuntimeError(f"Failed to load CSV for locust: {e}")

    @task
    def predict(self):
        if not self.data:
            return

        # pick a random row and send to /predict
        row = random.choice(self.data)

        # Convert empty strings to None and try to cast numeric fields
        payload = {}
        for k, v in row.items():
            if v is None or v == "":
                payload[k] = None
                continue
            # try to parse numbers
            try:
                if "." in v:
                    payload[k] = float(v)
                else:
                    payload[k] = int(v)
            except Exception:
                payload[k] = v

        headers = {"Content-Type": "application/json"}
        # Use a named endpoint so results aggregate under a single label in Locust
        self.client.post("/predict", json=payload, headers=headers, name="/predict")
