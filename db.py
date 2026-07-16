"""
db.py
-----
All SQLite database access lives here: schema creation, inserts,
and query helpers used by both the tracer (writer) and the
Streamlit dashboard (reader).
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

from config import DB_PATH


# ---------------------------------------------------------------
# CONNECTION HELPERS
# ---------------------------------------------------------------
@contextmanager
def get_connection():
    """Yield a SQLite connection with sane defaults, closing it afterward."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")  # allow tracer + dashboard to
                                               # read/write concurrently
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't already exist. Safe to call every run."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                latency_ms REAL,
                status TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds REAL,
                severity TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pings_target_time ON pings(target, timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_outages_target ON outages(target, start_time)")


# ---------------------------------------------------------------
# WRITE FUNCTIONS (used by tracer.py)
# ---------------------------------------------------------------
def insert_ping(target: str, latency_ms, status: str, timestamp: datetime = None):
    """Log one ping result."""
    ts = (timestamp or datetime.now()).isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO pings (target, timestamp, latency_ms, status) VALUES (?, ?, ?, ?)",
            (target, ts, latency_ms, status),
        )


def log_outage_start(target: str, start_time: datetime = None) -> int:
    """Insert a new outage row with no end_time yet. Returns the new row id."""
    ts = (start_time or datetime.now()).isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO outages (target, start_time) VALUES (?, ?)",
            (target, ts),
        )
        return cur.lastrowid


def log_outage_end(outage_id: int, end_time: datetime, severity: str):
    """Close out an open outage with its end time, duration, and severity."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT start_time FROM outages WHERE id = ?", (outage_id,)
        ).fetchone()
        if row is None:
            return
        start_time = datetime.fromisoformat(row["start_time"])
        duration = (end_time - start_time).total_seconds()
        conn.execute(
            "UPDATE outages SET end_time = ?, duration_seconds = ?, severity = ? WHERE id = ?",
            (end_time.isoformat(timespec="seconds"), duration, severity, outage_id),
        )


def get_open_outage(target: str):
    """Return the currently-open outage (no end_time) for a target, if any."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM outages WHERE target = ? AND end_time IS NULL "
            "ORDER BY start_time DESC LIMIT 1",
            (target,),
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------
# READ FUNCTIONS (used by app.py / analytics.py)
# ---------------------------------------------------------------
def get_recent_pings(target: str = None, limit: int = 500):
    """Return the most recent ping rows, optionally filtered by target."""
    with get_connection() as conn:
        if target and target != "All":
            rows = conn.execute(
                "SELECT * FROM pings WHERE target = ? ORDER BY timestamp DESC LIMIT ?",
                (target, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM pings ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_pings_in_range(target: str, start: str, end: str):
    """Return pings for a target between two ISO timestamps (inclusive)."""
    with get_connection() as conn:
        if target and target != "All":
            rows = conn.execute(
                "SELECT * FROM pings WHERE target = ? AND timestamp BETWEEN ? AND ? "
                "ORDER BY timestamp ASC",
                (target, start, end),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM pings WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC",
                (start, end),
            ).fetchall()
        return [dict(r) for r in rows]


def get_outages_by_range(target: str, start: str, end: str):
    """Return outages for a target (or all) that started within a date range."""
    with get_connection() as conn:
        if target and target != "All":
            rows = conn.execute(
                "SELECT * FROM outages WHERE target = ? AND start_time BETWEEN ? AND ? "
                "ORDER BY start_time DESC",
                (target, start, end),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM outages WHERE start_time BETWEEN ? AND ? ORDER BY start_time DESC",
                (start, end),
            ).fetchall()
        return [dict(r) for r in rows]


def get_all_targets_seen():
    """Return the distinct list of target names that have data logged."""
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT target FROM pings ORDER BY target").fetchall()
        return [r["target"] for r in rows]
