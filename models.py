from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PingResult:
    host: str
    sequence: int
    timestamp: datetime
    success: bool
    rtt_ms: Optional[float] = None
    error_type: Optional[str] = None


@dataclass
class OutageEvent:
    """
    DRAFT — added to unblock database.py integration.
    Please review/adjust field names or types as needed.

    Represents a single detected outage window for a host.
    """
    host: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
