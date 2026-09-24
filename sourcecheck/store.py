"""SQLite persistence. Runs and observations are immutable; review is append-only."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .config import DATA

def now():
    return datetime.now(timezone.utc).isoformat()

def uid():
    return uuid.uuid4().hex

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def decode(value):
    return json.loads(value) if value is not None else None

SCHEMA = """
PRAGMA foreign_keys=ON;
PRAGMA user_version=1;
CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, title TEXT NOT NULL, created TEXT NOT NULL, source_name TEXT NOT NULL, source_sha TEXT NOT NULL, source_kind TEXT NOT NULL, source_path TEXT NOT NULL, source_data TEXT NOT NULL, deleted INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS profiles(id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), version INTEGER NOT NULL, sha TEXT NOT NULL, document TEXT NOT NULL, created TEXT NOT NULL, UNIQUE(case_id,version));
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), profile_id TEXT NOT NULL REFERENCES profiles(id), previous_id TEXT REFERENCES runs(id), created TEXT NOT NULL, mode TEXT NOT NULL, adapter_version TEXT, destination_sha TEXT, destination_name TEXT, destination_path TEXT, destination_data TEXT, status TEXT NOT NULL, error TEXT, elapsed_ms REAL, findings TEXT, diff TEXT);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, started TEXT, finished TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS review_events(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), finding_id TEXT NOT NULL, reviewer TEXT NOT NULL, disposition TEXT NOT NULL, reason TEXT NOT NULL, created TEXT NOT NULL, origin TEXT NOT NULL DEFAULT 'human_reviewed');
CREATE TABLE IF NOT EXISTS reference_cases(id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), run_id TEXT NOT NULL REFERENCES runs(id), reviewer TEXT NOT NULL, origin TEXT NOT NULL, created TEXT NOT NULL, document TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS exports(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), created TEXT NOT NULL, review_cutoff TEXT NOT NULL, sha TEXT NOT NULL, path TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS semantic_runs(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), finding_id TEXT NOT NULL, status TEXT NOT NULL, request_sha TEXT NOT NULL, response TEXT, usage TEXT, elapsed_ms REAL, created TEXT NOT NULL);
"""

@contextmanager
def db():
    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DATA / "sourcecheck.sqlite", timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        con.executescript(SCHEMA)
        if "origin" not in {item[1] for item in con.execute("PRAGMA table_info(review_events)")}:
            con.execute("ALTER TABLE review_events ADD COLUMN origin TEXT NOT NULL DEFAULT 'human_reviewed'")
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def row(con, sql, params=()):
    found = con.execute(sql, params).fetchone()
    return dict(found) if found else None

def rows(con, sql, params=()):
    return [dict(item) for item in con.execute(sql, params)]

def save_bytes(kind, value):
    directory = DATA / kind
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / uid()
    path.write_bytes(value)
    return str(path)
