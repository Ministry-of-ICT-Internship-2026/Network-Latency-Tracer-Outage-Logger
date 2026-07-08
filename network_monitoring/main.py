"""
Example entry point for the network monitoring module.

Run directly to monitor the configured hosts and print rolling status
summaries every few seconds. Replace `on_result` with a call into the
outage-logger module once it exists.
"""
import asyncio
import logging

from config import MonitorConfig
from models import HostStatus, PingResult
from monitor import NetworkMonitor
from outage import OutageManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

outage_manager = OutageManager()

def on_result(result: PingResult, status: HostStatus) -> None:

    outage_event = outage_manager.process(result, status)

    outcome = (
        f"{result.rtt_ms:.1f} ms"
        if result.success
        else f"FAILED ({result.error_type})"
    )

    print(
        f"[{result.host}] "
        f"seq={result.sequence} "
        f"{outcome} | "
        f"loss={status.loss_rate:.1f}% "
        f"avg_rtt={status.avg_rtt} "
        f"outage={status.is_outage}"
    )

    if outage_event:
        print("\n========== OUTAGE COMPLETED ==========")
        print(f"Host: {outage_event.host}")
        print(f"Started: {outage_event.start_time}")
        print(f"Ended: {outage_event.end_time}")
        print(
            f"Duration: "
            f"{outage_event.duration_seconds:.2f} seconds"
        )
        print("======================================\n")


async def main():
    config = MonitorConfig(
        hosts=["8.8.8.8", "1.1.1.1"],
        interval_seconds=3.0,
        timeout_seconds=2.0,
        window_size=10,
        outage_threshold=3,
    )
    monitor = NetworkMonitor(config, on_result=on_result)

    try:
        await monitor.start()
    except KeyboardInterrupt:
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
