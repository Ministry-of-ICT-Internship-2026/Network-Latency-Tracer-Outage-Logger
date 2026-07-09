import sqlite3
from pathlib import Path
from typing import List
from models import PingResult, OutageEvent


class DatabaseManager:
    

    def __init__(self, db_path: str = "database/latency.db"):
        # Ensure the database folder exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    
    def create_tables(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS latency_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            latency_ms REAL,
            error_type TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS outage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_seconds REAL NOT NULL
        )
        """)
        self.connection.commit()

   
    def save_ping(self, result: PingResult) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO latency_logs
        (
            host,
            sequence,
            timestamp,
            success,
            latency_ms,
            error_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            result.host,
            result.sequence,
            result.timestamp.isoformat(),
            int(result.success),
            result.rtt_ms,
            result.error_type
        ))
        self.connection.commit()

    
    def save_outage(self, outage: OutageEvent) -> None:
        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO outage_logs
        (
            host,
            start_time,
            end_time,
            duration_seconds
        )
        VALUES (?, ?, ?, ?)
        """, (
            outage.host,
            outage.start_time.isoformat(),
            outage.end_time.isoformat(),
            outage.duration_seconds
        ))
        self.connection.commit()

    
    def get_ping_history(self, host: str) -> List[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT *
        FROM latency_logs
        WHERE host = ?
        ORDER BY timestamp ASC
        """, (host,))
        return cursor.fetchall()

    
    def get_outages(self, host: str) -> List[sqlite3.Row]:
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT *
        FROM outage_logs
        WHERE host = ?
        ORDER BY start_time ASC
        """, (host,))
        return cursor.fetchall()

    
    def get_latest_status(self, host: str):
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT *
        FROM latency_logs
        WHERE host = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """, (host,))
        return cursor.fetchone()

    
    def close(self) -> None:
        self.connection.close()
