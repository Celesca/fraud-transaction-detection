"""Database helper functions for fraud storage (SQLite)
"""
import sqlite3
import os
import json
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "frauds.db")

def init_db(db_path: str | None = None) -> None:
    """Create the database and frauds table if it doesn't exist."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS frauds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_data TEXT,
            fraud_probability REAL,
            prediction_time TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_fraud_to_db(transaction: Dict, probability: float, prediction_time: str, db_path: str | None = None) -> None:
    """Insert a fraudulent transaction record into the DB."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO frauds (transaction_data, fraud_probability, prediction_time)
        VALUES (?, ?, ?)
        """,
        (
            json.dumps(transaction),
            float(probability),
            prediction_time,
        ),
    )
    conn.commit()
    conn.close()


def get_all_frauds(db_path: str | None = None) -> List[Dict]:
    """Return all fraud records as list of dicts."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, transaction_data, fraud_probability, prediction_time FROM frauds"
    )
    rows = cursor.fetchall()
    conn.close()

    result: List[Dict] = []
    for row in rows:
        result.append(
            {
                "id": row[0],
                "transaction_data": json.loads(row[1]) if row[1] else {},
                "fraud_probability": row[2],
                "prediction_time": row[3],
            }
        )
    return result


def clear_frauds(db_path: str | None = None) -> int:
    """Delete all fraud records and return number of deleted rows."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM frauds")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted
