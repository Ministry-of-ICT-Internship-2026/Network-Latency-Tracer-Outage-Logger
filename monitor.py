from __future__ import annotations

import platform
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from latency_tracer.config import Settings, Target
from latency_tracer.database import (
    close_open_outage,
    connect,
    get_open_outage,
    initialize_database,
    insert_check,
    open_outage,
    update_open_outage,
)
from latency_tracer.detector import DetectionDecision, DetectionPolicy, evaluate_check


LATENCY_PATTERNS = [
    re.compile(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", re.IGNORECASE),
    re.compile(r"Average\s*=\s*(\d+(?:\.\d+)?)ms", re.IGNORECASE),
    re.compile(r"avg[/=]\s*(\d+(?:\.\d+)?)", re.IGNORECASE),
]


@dataclass(frozen=True)
class PingResult:
    checked_at: str
    target: Target
    status: str
    latency_ms: float | None
    packet_loss_percent: float
    error: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ping_target(target: Target, timeout_seconds: int) -> PingResult:
    checked_at = utc_now()
    command = _ping_command(target.host, timeout_seconds)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return PingResult(
            checked_at=checked_at,
            target=target,
            status="down",
            latency_ms=None,
            packet_loss_percent=100,
            error="Ping timed out",
        )
    except OSError as exc:
        return PingResult(
            checked_at=checked_at,
            target=target,
            status="down",
            latency_ms=None,
            packet_loss_percent=100,
            error=str(exc),
        )

    output = f"{completed.stdout}\n{completed.stderr}"
    latency_ms = _extract_latency(output)

    if completed.returncode == 0:
        return PingResult(
            checked_at=checked_at,
            target=target,
            status="up",
            latency_ms=latency_ms,
            packet_loss_percent=0,
        )

    return PingResult(
        checked_at=checked_at,
        target=target,
        status="down",
        latency_ms=latency_ms,
        packet_loss_percent=100,
        error=_summarize_error(output),
    )


def run_monitor(settings: Settings) -> None:
    initialize_database(settings.database_path)
    consecutive_failures: dict[str, int] = {}
    policy = DetectionPolicy(
        failure_threshold=settings.failure_threshold,
        latency_warning_ms=settings.latency_warning_ms,
    )

    print("Network Latency Tracer started. Press Ctrl+C to stop.")
    print(f"Database: {settings.database_path}")
    print(f"Targets: {', '.join(target.name for target in settings.targets)}")

    while True:
        with connect(settings.database_path) as conn:
            for target in settings.targets:
                result = ping_target(target, settings.ping_timeout_seconds)
                key = f"{target.name}|{target.host}"

                if result.status == "down":
                    consecutive_failures[key] = consecutive_failures.get(key, 0) + 1
                else:
                    consecutive_failures[key] = 0

                decision = evaluate_check(
                    raw_status=result.status,
                    latency_ms=result.latency_ms,
                    error=result.error,
                    consecutive_failures=consecutive_failures[key],
                    policy=policy,
                )
                insert_check(
                    conn,
                    checked_at=result.checked_at,
                    target_name=target.name,
                    host=target.host,
                    status=decision.status,
                    latency_ms=result.latency_ms,
                    packet_loss_percent=result.packet_loss_percent,
                    error=result.error,
                )
                _update_outage_state(conn, result, decision, consecutive_failures[key])

                latency = "n/a" if result.latency_ms is None else f"{result.latency_ms:.1f} ms"
                print(f"{result.checked_at} {target.name} {decision.status} {latency}")

        time.sleep(settings.check_interval_seconds)


def _update_outage_state(
    conn,
    result: PingResult,
    decision: DetectionDecision,
    failures: int,
) -> None:
    target = result.target

    if decision.should_close_outage:
        close_open_outage(
            conn,
            target_name=target.name,
            host=target.host,
            ended_at=result.checked_at,
        )
        return

    if not decision.should_open_outage:
        return

    open_event = get_open_outage(conn, target_name=target.name, host=target.host)
    if open_event:
        update_open_outage(
            conn,
            outage_id=int(open_event["id"]),
            failure_count=failures,
            max_latency_ms=result.latency_ms,
        )
    else:
        open_outage(
            conn,
            target_name=target.name,
            host=target.host,
            started_at=result.checked_at,
            failure_count=failures,
            max_latency_ms=result.latency_ms,
            reason=decision.reason or "Consecutive ping failures",
        )


def _ping_command(host: str, timeout_seconds: int) -> list[str]:
    if platform.system().lower() == "windows":
        return ["ping", "-n", "1", "-w", str(timeout_seconds * 1000), host]
    return ["ping", "-c", "1", "-W", str(timeout_seconds), host]


def _extract_latency(output: str) -> float | None:
    for pattern in LATENCY_PATTERNS:
        match = pattern.search(output)
        if match:
            return float(match.group(1))
    return None


def _summarize_error(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else "Ping failed"
