"""Append-only through the application API; not a tamper-proof compliance ledger."""
import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from .governance import propose, resolve, ReviewError

class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS evaluations (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, body TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS proposals (id TEXT PRIMARY KEY, evaluation_id TEXT NOT NULL, body TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS review_events (id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL, body TEXT NOT NULL)")
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

    def propose_review(self, evaluation_id, payload):
        evaluation = self.get(evaluation_id)
        if not evaluation:
            raise KeyError('Evaluation not found')
        proposal = propose(evaluation, payload)
        with self.connect() as db:
            db.execute("INSERT INTO proposals VALUES (?, ?, ?)", (proposal['id'], evaluation_id, json.dumps(proposal)))
            db.execute("INSERT INTO review_events VALUES (?, ?, ?)", (str(uuid4()), proposal['id'], json.dumps(proposal)))
        return proposal

    def resolve_review(self, proposal_id, payload):
        with self.connect() as db:
            # Serialize competing resolutions before reading the pending state.
            db.execute('BEGIN IMMEDIATE')
            row = db.execute("SELECT body FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            if not row:
                raise KeyError('Proposal not found')
            result = resolve(json.loads(row[0]), payload)
            db.execute("UPDATE proposals SET body = ? WHERE id = ?", (json.dumps(result), proposal_id))
            db.execute("INSERT INTO review_events VALUES (?, ?, ?)", (str(uuid4()), proposal_id, json.dumps(result)))
        return result

    def review_history(self, evaluation_id):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute(
                "SELECT e.body FROM review_events e JOIN proposals p ON e.proposal_id = p.id WHERE p.evaluation_id = ? ORDER BY e.rowid", (evaluation_id,))]
