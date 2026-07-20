import sqlite3
from pathlib import Path
from typing import List

from monitoring.models import PingResult, OutageEvent


class DatabaseManager:

    def __init__(
        self,
        db_path: str = "database/latency.db"
    ):

        Path(db_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

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

            duration_seconds REAL NOT NULL,

            reason TEXT

        )
        """)



        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hosts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hostname TEXT NOT NULL,

            ip_address TEXT NOT NULL UNIQUE,

            enabled INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)



        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_latency_host
        ON latency_logs(host)
        """)



        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_outage_host
        ON outage_logs(host)
        """)


        self.connection.commit()




    # ------------------------------------------------
    # LATENCY
    # ------------------------------------------------


    def save_ping(
        self,
        result: PingResult
    ) -> None:


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

        """,

        (
            result.host,
            result.sequence,
            result.timestamp.isoformat(),
            int(result.success),
            result.rtt_ms,
            result.error_type
        ))


        self.connection.commit()




    # ------------------------------------------------
    # OUTAGES
    # ------------------------------------------------


    def save_outage(
        self,
        outage: OutageEvent,
        reason: str = "Consecutive ping failures"
    ):


        cursor = self.connection.cursor()


        cursor.execute("""
        INSERT INTO outage_logs
        (
            host,
            start_time,
            end_time,
            duration_seconds,
            reason
        )

        VALUES (?, ?, ?, ?, ?)

        """,

        (
            outage.host,
            outage.start_time.isoformat(),
            outage.end_time.isoformat(),
            outage.duration_seconds,
            reason
        ))


        self.connection.commit()




    # ------------------------------------------------
    # HISTORY
    # ------------------------------------------------


    def get_ping_history(
        self,
        host: str
    ) -> List[sqlite3.Row]:


        cursor = self.connection.cursor()


        cursor.execute("""
        SELECT *
        FROM latency_logs

        WHERE host = ?

        ORDER BY timestamp ASC

        """,

        (host,))


        return cursor.fetchall()




    def get_outages(
        self,
        host: str
    ) -> List[sqlite3.Row]:


        cursor = self.connection.cursor()


        cursor.execute("""
        SELECT *

        FROM outage_logs

        WHERE host = ?

        ORDER BY start_time ASC

        """,

        (host,))


        return cursor.fetchall()




    def get_latest_status(
        self,
        host: str
    ):


        cursor = self.connection.cursor()


        cursor.execute("""
        SELECT *

        FROM latency_logs

        WHERE host = ?

        ORDER BY timestamp DESC

        LIMIT 1

        """,

        (host,))


        return cursor.fetchone()




    # ------------------------------------------------
    # HOST MANAGEMENT
    # ------------------------------------------------


    def add_host(
        self,
        hostname,
        ip_address
    ):


        try:

            self.connection.execute(
            """

            INSERT INTO hosts
            (
                hostname,
                ip_address,
                enabled
            )

            VALUES (?, ?, 1)

            """,

            (
                hostname,
                ip_address
            ))


            self.connection.commit()


            return True, "Host added successfully"



        except sqlite3.IntegrityError:


            return False, "Host already exists"




    # Get ALL hosts for dashboard

    def get_hosts(self):


        cursor = self.connection.execute(
        """

        SELECT *

        FROM hosts

        ORDER BY id ASC

        """
        )


        return cursor.fetchall()




    # Get only active hosts for monitoring

    def get_enabled_hosts(self):


        cursor = self.connection.execute(
        """

        SELECT *

        FROM hosts

        WHERE enabled = 1

        """
        )


        return cursor.fetchall()




    # Enable / Disable host

    def toggle_host(
        self,
        host_id
    ):


        cursor = self.connection.cursor()


        cursor.execute(
        """

        UPDATE hosts

        SET enabled =

            CASE

                WHEN enabled = 1 THEN 0

                ELSE 1

            END


        WHERE id = ?

        """,

        (host_id,))


        self.connection.commit()



        return cursor.rowcount > 0




    def delete_host(
        self,
        host_id
    ):


        self.connection.execute(
        """

        DELETE FROM hosts

        WHERE id = ?

        """,

        (host_id,))


        self.connection.commit()




    # ------------------------------------------------
    # CLEANUP
    # ------------------------------------------------


    def clear_latency_logs(self):


        self.connection.execute(
        """

        DELETE FROM latency_logs

        """
        )


        self.connection.commit()




    def clear_outage_logs(self):


        self.connection.execute(
        """

        DELETE FROM outage_logs

        """
        )


        self.connection.commit()




    def clear_all_logs(self):

        self.clear_latency_logs()

        self.clear_outage_logs()




    def delete_host_data(
        self,
        host
    ):


        self.connection.execute(
        """

        DELETE FROM latency_logs

        WHERE host = ?

        """,

        (host,))


        self.connection.execute(
        """

        DELETE FROM outage_logs

        WHERE host = ?

        """,

        (host,))


        self.connection.commit()




    def close(self):

        self.connection.close()