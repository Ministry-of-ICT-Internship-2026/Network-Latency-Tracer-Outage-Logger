from __future__ import annotations

import sqlite3
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional



def _parse_ts(value: str) -> datetime:
    """Parses the ISO timestamps written by database.py (always UTC)."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _percentile(sorted_values: List[float], pct: float) -> Optional[float]:
    """Nearest-rank percentile. pct in [0, 100]. Empty input -> None."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


@dataclass
class HostReport:
    host: str
    total_pings: int = 0
    successful_pings: int = 0
    failed_pings: int = 0
    uptime_pct: float = 100.0
    avg_latency_ms: Optional[float] = None
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    stdev_latency_ms: Optional[float] = None
    avg_jitter_ms: Optional[float] = None
    outage_count: int = 0
    total_downtime_seconds: float = 0.0
    mttr_seconds: Optional[float] = None     # mean time to recovery (per completed outage)
    mtbf_seconds: Optional[float] = None      # mean time between failures
    longest_outage_seconds: Optional[float] = None
    currently_down: bool = False
    current_consecutive_failures: int = 0
    error_breakdown: Dict[str, int] = field(default_factory=dict)
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    reliability_grade: str = "N/A"
    latency_series: List[dict] = field(default_factory=list)   # bucketed for charts
    loss_series: List[dict] = field(default_factory=list)
    outages: List[dict] = field(default_factory=list)


def _grade(uptime_pct: float) -> str:
    """Maps availability to a simple accountability-friendly grade."""
    if uptime_pct >= 99.9:
        return "Excellent"
    if uptime_pct >= 99.0:
        return "Good"
    if uptime_pct >= 95.0:
        return "Fair"
    if uptime_pct >= 90.0:
        return "Poor"
    return "Critical"


def _bucket_key(dt: datetime, bucket_seconds: int) -> datetime:
    epoch = dt.timestamp()
    bucketed = epoch - (epoch % bucket_seconds)
    return datetime.fromtimestamp(bucketed, tz=timezone.utc)


class MonitoringAnalytics:
    """
    Computes report-ready analytics directly from the SQLite database.
    Read-only: never mutates latency_logs / outage_logs.
    """

    def __init__(self, db_path: str = "database/latency.db", outage_threshold: int = 3):
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found at: {db_path}")
        self.db_path = db_path
        self.outage_threshold = outage_threshold
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "MonitoringAnalytics":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_hosts(self) -> List[str]:
        cur = self.connection.cursor()
        cur.execute("SELECT DISTINCT host FROM latency_logs ORDER BY host")
        return [row["host"] for row in cur.fetchall()]

    def build_full_report(self, bucket_seconds: int = 60) -> dict:
        """
        Returns the full analytics payload used by report_generator.py:
        {
          "generated_at": ...,
          "period": {"start": ..., "end": ..., "duration_hours": ...},
          "summary": {...},                # fleet-wide rollup
          "hosts": {host: HostReport-as-dict, ...},
          "error_breakdown": {...},        # fleet-wide
          "outage_log": [...],             # every completed outage, all hosts, chronological
        }
        """
        hosts = self.get_hosts()
        host_reports = {host: self._build_host_report(host, bucket_seconds) for host in hosts}

        period = self._get_period()
        summary = self._build_summary(host_reports, period)
        fleet_errors: Dict[str, int] = {}
        outage_log: List[dict] = []
        for hr in host_reports.values():
            for err, count in hr.error_breakdown.items():
                fleet_errors[err] = fleet_errors.get(err, 0) + count
            outage_log.extend(hr.outages)
        outage_log.sort(key=lambda o: o["start_time"])

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": period,
            "summary": summary,
            "hosts": {h: self._host_report_to_dict(r) for h, r in host_reports.items()},
            "error_breakdown": fleet_errors,
            "outage_log": outage_log,
        }
    
    def get_latency_logs(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM latency_logs
            ORDER BY timestamp
        """)

        return cursor.fetchall()

        return cursor.fetchall()


    def get_outage_logs(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM outage_logs
            ORDER BY start_time
        """)

        return cursor.fetchall()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_period(self) -> dict:
        cur = self.connection.cursor()
        cur.execute("SELECT MIN(timestamp) AS start, MAX(timestamp) AS end FROM latency_logs")
        row = cur.fetchone()
        if not row or not row["start"]:
            return {"start": None, "end": None, "duration_hours": 0.0}
        start = _parse_ts(row["start"])
        end = _parse_ts(row["end"])
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "duration_hours": round((end - start).total_seconds() / 3600, 2),
        }

    def _build_summary(self, host_reports: Dict[str, HostReport], period: dict) -> dict:
        total_pings = sum(h.total_pings for h in host_reports.values())
        total_failed = sum(h.failed_pings for h in host_reports.values())
        total_outages = sum(h.outage_count for h in host_reports.values())
        total_downtime = sum(h.total_downtime_seconds for h in host_reports.values())

        uptimes = [h.uptime_pct for h in host_reports.values() if h.total_pings > 0]
        latencies = [h.avg_latency_ms for h in host_reports.values() if h.avg_latency_ms is not None]

        worst_host = min(
            (h for h in host_reports.values() if h.total_pings > 0),
            key=lambda h: h.uptime_pct,
            default=None,
        )
        best_host = max(
            (h for h in host_reports.values() if h.total_pings > 0),
            key=lambda h: h.uptime_pct,
            default=None,
        )
        currently_down = [h.host for h in host_reports.values() if h.currently_down]

        return {
            "hosts_monitored": len(host_reports),
            "total_pings": total_pings,
            "total_failed_pings": total_failed,
            "fleet_uptime_pct": round(sum(uptimes) / len(uptimes), 2) if uptimes else 100.0,
            "fleet_avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "total_outages": total_outages,
            "total_downtime_seconds": round(total_downtime, 1),
            "total_downtime_human": _human_duration(total_downtime),
            "worst_host": worst_host.host if worst_host else None,
            "worst_host_uptime_pct": worst_host.uptime_pct if worst_host else None,
            "best_host": best_host.host if best_host else None,
            "best_host_uptime_pct": best_host.uptime_pct if best_host else None,
            "currently_down_hosts": currently_down,
            "monitoring_window_hours": period["duration_hours"],
        }

    def _build_host_report(self, host: str, bucket_seconds: int) -> HostReport:
        cur = self.connection.cursor()
        cur.execute(
            """
            SELECT sequence, timestamp, success, latency_ms, error_type
            FROM latency_logs
            WHERE host = ?
            ORDER BY timestamp ASC
            """,
            (host,),
        )
        rows = cur.fetchall()

        report = HostReport(host=host)
        report.total_pings = len(rows)
        if not rows:
            return report

        successes = [r for r in rows if r["success"]]
        failures = [r for r in rows if not r["success"]]
        report.successful_pings = len(successes)
        report.failed_pings = len(failures)
        report.uptime_pct = round((len(successes) / len(rows)) * 100, 2) if rows else 100.0
        report.first_seen = rows[0]["timestamp"]
        report.last_seen = rows[-1]["timestamp"]
        report.reliability_grade = _grade(report.uptime_pct)

        latencies = sorted(r["latency_ms"] for r in successes if r["latency_ms"] is not None)
        if latencies:
            report.avg_latency_ms = round(sum(latencies) / len(latencies), 2)
            report.min_latency_ms = round(min(latencies), 2)
            report.max_latency_ms = round(max(latencies), 2)
            report.p95_latency_ms = round(_percentile(latencies, 95), 2)
            if len(latencies) > 1:
                report.stdev_latency_ms = round(statistics.stdev(latencies), 2)

        ordered_success_latencies = [
            r["latency_ms"] for r in successes if r["latency_ms"] is not None
        ]
        if len(ordered_success_latencies) > 1:
            diffs = [
                abs(ordered_success_latencies[i] - ordered_success_latencies[i - 1])
                for i in range(1, len(ordered_success_latencies))
            ]
            report.avg_jitter_ms = round(sum(diffs) / len(diffs), 2)

        error_breakdown: Dict[str, int] = {}
        for r in failures:
            key = r["error_type"] or "unknown"
            error_breakdown[key] = error_breakdown.get(key, 0) + 1
        report.error_breakdown = error_breakdown

        # ---- Outage reconstruction (consecutive-failure windows) ----
        outages, current_streak, currently_down = self._reconstruct_outages(rows)
        report.outages = outages
        report.outage_count = len(outages)
        report.current_consecutive_failures = current_streak
        report.currently_down = currently_down
        if outages:
            durations = [o["duration_seconds"] for o in outages]
            report.total_downtime_seconds = round(sum(durations), 1)
            report.longest_outage_seconds = round(max(durations), 1)

            completed = [o for o in outages if not o.get("ongoing")]
            if completed:
                completed_durations = [o["duration_seconds"] for o in completed]
                report.mttr_seconds = round(sum(completed_durations) / len(completed_durations), 1)
            if len(outages) > 1:
                gaps = [
                    (
                        _parse_ts(outages[i]["start_time"]) - _parse_ts(outages[i - 1]["end_time"])
                    ).total_seconds()
                    for i in range(1, len(outages))
                ]
                report.mtbf_seconds = round(sum(gaps) / len(gaps), 1) if gaps else None

        # ---- Time-bucketed series for charts ----
        report.latency_series = self._bucket_latency(rows, bucket_seconds)
        report.loss_series = self._bucket_loss(rows, bucket_seconds)

        return report

    def _reconstruct_outages(
    self,
    rows: List[sqlite3.Row],
) -> tuple[List[dict], int, bool]:
        """
        Rebuilds outage windows the same way outage.py/HostStatus do at
        runtime (>= outage_threshold consecutive failures = outage),
        purely from the historical log. This lets the report count
        outages even if the live process was stopped mid-outage (so
        outage_logs never received a completed row), and flags a host
        as "currently down" if it ends the log on an active failure
        streak.
        """
        outages: List[dict] = []
        consecutive = 0
        outage_start: Optional[str] = None
        in_outage = False

        for row in rows:
            if row["success"]:
                if in_outage:
                    outages.append(
                        {
                            "host": row["host"] if "host" in row.keys() else None,
                            "start_time": outage_start,
                            "end_time": row["timestamp"],
                            "duration_seconds": round(
                                (_parse_ts(row["timestamp"]) - _parse_ts(outage_start)).total_seconds(),
                                1,
                            ),
                        }
                    )
                    in_outage = False
                    outage_start = None
                consecutive = 0
            else:
                consecutive += 1
                if consecutive == self.outage_threshold:
                    # the outage started `outage_threshold - 1` failures back
                    start_idx = rows.index(row) - (self.outage_threshold - 1)
                    outage_start = rows[start_idx]["timestamp"]
                    in_outage = True

        currently_down = in_outage
        if in_outage:
            # Host is still down as of the last log entry - record the
            # in-progress outage so it shows up in outage history/tables
            # even though it hasn't recovered yet.
            now = datetime.now(timezone.utc)
            outages.append(
                {
                    "host": None,
                    "start_time": outage_start,
                    "end_time": None,
                    "ongoing": True,
                    "duration_seconds": round(
                        (now - _parse_ts(outage_start)).total_seconds(), 1
                    ),
                }
            )
        return outages, consecutive, currently_down

    def _bucket_latency(self, rows: List[sqlite3.Row], bucket_seconds: int) -> List[dict]:
        buckets: Dict[datetime, List[float]] = {}
        for r in rows:
            if not r["success"] or r["latency_ms"] is None:
                continue
            key = _bucket_key(_parse_ts(r["timestamp"]), bucket_seconds)
            buckets.setdefault(key, []).append(r["latency_ms"])
        return [
            {"t": k.isoformat(), "avg_ms": round(sum(v) / len(v), 2), "samples": len(v)}
            for k, v in sorted(buckets.items())
        ]

    def _bucket_loss(self, rows: List[sqlite3.Row], bucket_seconds: int) -> List[dict]:
        buckets: Dict[datetime, List[bool]] = {}
        for r in rows:
            key = _bucket_key(_parse_ts(r["timestamp"]), bucket_seconds)
            buckets.setdefault(key, []).append(bool(r["success"]))
        out = []
        for k, v in sorted(buckets.items()):
            failed = sum(1 for s in v if not s)
            out.append(
                {
                    "t": k.isoformat(),
                    "loss_pct": round((failed / len(v)) * 100, 1),
                    "samples": len(v),
                }
            )
        return out

    @staticmethod
    def _host_report_to_dict(report: HostReport) -> dict:
        d = report.__dict__.copy()
        # host field already carried on the report; strip duplicate outages->host None values
        for o in d["outages"]:
            o["host"] = report.host
        return d


def _human_duration(total_seconds: float) -> str:
    if total_seconds <= 0:
        return "0s"
    seconds = int(total_seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


if __name__ == "__main__":
    import json
    import sys

    db = sys.argv[1] if len(sys.argv) > 1 else "database/latency.db"
    with MonitoringAnalytics(db) as analytics:
        print(json.dumps(analytics.build_full_report(), indent=2, default=str))
