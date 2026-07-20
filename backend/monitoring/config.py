"""
config.py
---------
Central configuration for the Network Latency Tracer & Outage Logger.

All monitoring settings are managed here.
"""

from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------
# Targets
# ---------------------------------------------------------------

@dataclass
class Target:

    name: str
    host: str



# ---------------------------------------------------------------
# Monitor Configuration
# ---------------------------------------------------------------

@dataclass
class MonitorConfig:

    # Targets loaded from database
    targets: list[Target] = field(
        default_factory=list
    )


    # Timing
    interval_seconds: float = 5.0

    timeout_seconds: float = 2.0


    # Statistics
    window_size: int = 10


    # Outage detection
    outage_threshold: int = 3


    # Reliability thresholds
    degraded_latency_ms: float = 150.0

    major_outage_seconds: int = 300


    # SLA
    sla_target_percent: float = 99.5


    # Database
    database_path: Path = Path(
        "database/latency.db"
    )


    # Dashboard
    dashboard_refresh_seconds: int = 5



config = MonitorConfig()



def load_targets_from_database():

    from monitoring.database import DatabaseManager

    db = DatabaseManager()

    try:

        hosts = db.get_enabled_hosts()
        print("Hosts from database:", hosts)

        return [

            Target(
                name=host["hostname"],
                host=host["ip_address"]
            )

            for host in hosts

        ]

    finally:

        db.close()