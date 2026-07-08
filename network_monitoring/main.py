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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def on_result(result: PingResult, status: HostStatus) -> None:
    outcome = f"{result.rtt_ms:.1f} ms" if result.success else f"FAILED ({result.error_type})"
    print(f"[{result.host}] seq={result.sequence} {outcome} | "
          f"loss={status.loss_rate:.1f}% avg_rtt={status.avg_rtt} outage={status.is_outage}")


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
