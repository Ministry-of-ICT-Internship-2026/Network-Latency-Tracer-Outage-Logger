from dataclasses import dataclass
from datetime import datetime
from collections import deque
from typing import Optional, Deque


@dataclass
class PingResult:
    host: str
    sequence: int
    timestamp: datetime
    success: bool
    rtt_ms: Optional[float]
    error_type: Optional[str]  # None | "timeout" | "unreachable" | "permission_denied"

@dataclass
class OutageEvent:
    """
    Represents a completed network outage.
    """

    host: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    reason: str = "Consecutive ping failures"

class HostStatus:


    def __init__(self, host: str, window_size: int = 10, outage_threshold: int = 3):
        self.host = host
        self.window_size = window_size
        self.outage_threshold = outage_threshold
        self._results: Deque[PingResult] = deque(maxlen=window_size)
        self.consecutive_failures: int = 0

    def record(self, result: PingResult) -> None:
        self._results.append(result)
        if result.success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1

    @property
    def loss_rate(self) -> float:
        """Percentage of probes in the current window that failed."""
        if not self._results:
            return 0.0
        failures = sum(1 for r in self._results if not r.success)
        return failures / len(self._results) * 100

    @property
    def avg_rtt(self) -> Optional[float]:
        rtts = [r.rtt_ms for r in self._results if r.success and r.rtt_ms is not None]
        if not rtts:
            return None
        return sum(rtts) / len(rtts)

    @property
    def jitter(self) -> Optional[float]:
        """Mean absolute difference between consecutive successful RTTs (ms)."""
        rtts = [r.rtt_ms for r in self._results if r.success and r.rtt_ms is not None]
        if len(rtts) < 2:
            return None
        diffs = [abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))]
        return sum(diffs) / len(diffs)

    @property
    def is_outage(self) -> bool:
        return self.consecutive_failures >= self.outage_threshold

    @property
    def last_result(self) -> Optional[PingResult]:
        return self._results[-1] if self._results else None

    def summary(self) -> dict:
        return {
            "host": self.host,
            "loss_rate_pct": round(self.loss_rate, 2),
            "avg_rtt_ms": round(self.avg_rtt, 2) if self.avg_rtt is not None else None,
            "jitter_ms": round(self.jitter, 2) if self.jitter is not None else None,
            "consecutive_failures": self.consecutive_failures,
            "is_outage": self.is_outage,
            "samples_in_window": len(self._results),
        }
