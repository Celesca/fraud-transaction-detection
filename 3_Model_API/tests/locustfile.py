from locust import HttpUser, task, between
import csv
import os
import random
import json
from typing import List, Dict
import logging
from threading import Lock


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
    # simple counter to allow printing the first few payloads for debugging
    _print_lock = Lock()
    _sent_counter: int = 0
    _max_prints: int = 5

    # configure logger for this locustfile
    logger = logging.getLogger("locustfile")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] locust: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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

        # Convert CSV row to payload matching the API Transaction schema.
        # Normalize header names (common aliases) and values (enum strings).
        payload = {}
        for k, v in row.items():
            key = k.strip()
            if not key:
                continue

            # normalize common header aliases to API field names
            key_lower = key.lower()
            if key_lower in ("time", "timestamp"):
                key = "time_ind"
            elif key_lower in ("type", "transaction_type"):
                key = "transac_type"
            elif key_lower in ("src_account", "src_account_id"):
                key = "src_acc"
            elif key_lower in ("dst_account", "dst_account_id"):
                key = "dst_acc"

            # empty -> None
            if v is None or v == "":
                payload[key] = None
                continue

            # If value looks like an Enum repr e.g. "TRANSAC_TYPE.CASH_IN", take last part
            if isinstance(v, str) and "." in v and v.split(".")[0].isupper():
                v = v.split(".")[-1]

            # attempt numeric conversion when appropriate
            if isinstance(v, str):
                vs = v.strip()
            else:
                vs = v

            if isinstance(vs, str):
                try:
                    if "." in vs:
                        parsed = float(vs)
                    else:
                        parsed = int(vs)
                    payload[key] = parsed
                    continue
                except Exception:
                    # keep as string
                    payload[key] = vs
                    continue

            payload[key] = v

        headers = {"Content-Type": "application/json"}

        # Print/Log the first few payloads to help debug 4xx errors
        with self._print_lock:
            if self._sent_counter < self._max_prints:
                self.logger.info("Sending payload #%d: %s", self._sent_counter + 1, json.dumps(payload))
            self._sent_counter += 1

        # Use catch_response to inspect server response and log on failures
        with self.client.post("/predict", json=payload, headers=headers, name="/predict", catch_response=True) as resp:
            try:
                status = resp.status_code
            except Exception:
                status = None

            if status is None or status >= 400:
                # log full payload and response body for debugging
                try:
                    body_text = resp.text
                except Exception:
                    body_text = "<no response body>"
                self.logger.error("Request failed (status=%s). Payload: %s Response: %s", status, json.dumps(payload), body_text)
                # mark as failure so Locust records it
                resp.failure(f"HTTP {status}")
