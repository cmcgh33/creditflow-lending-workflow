"""Append-only through the application API; not a tamper-proof compliance ledger."""
import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS evaluations (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, body TEXT NOT NULL)")
    def connect(self):
        return sqlite3.connect(self.path, timeout=10)
    def save(self, result):
        record = {**result, "id": str(uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}
        with self.connect() as db:
            db.execute("INSERT INTO evaluations VALUES (?, ?, ?)", (record["id"], record["created_at"], json.dumps(record, allow_nan=False)))
        return record
    def list(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT body FROM evaluations ORDER BY created_at DESC, id DESC LIMIT 100")]
    def get(self, record_id):
        with self.connect() as db:
            row = db.execute("SELECT body FROM evaluations WHERE id = ?", (record_id,)).fetchone()
        return json.loads(row[0]) if row else None
