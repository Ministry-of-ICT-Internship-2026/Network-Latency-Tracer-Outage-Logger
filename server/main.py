import asyncio
import logging

from config import MonitorConfig
from models import HostStatus, PingResult
from monitor import NetworkMonitor
from outage import OutageManager
from database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

database = DatabaseManager()
outage_manager = OutageManager()


def on_result(result: PingResult, status: HostStatus) -> None:
    # Save every ping result
    database.save_ping(result)

    # Check whether an outage has completed
    outage = outage_manager.process(result, status)

    if outage:
        database.save_outage(outage)

        print("\n========== OUTAGE RECORDED ==========")
        print(f"Host: {outage.host}")
        print(f"Started: {outage.start_time}")
        print(f"Ended: {outage.end_time}")
        print(f"Duration: {outage.duration_seconds:.2f} seconds")
        print("=====================================\n")

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


async def main():
    config = MonitorConfig(
        hosts=[
            "8.8.8.8",
            "1.1.1.1",
            "192.0.2.1",
        ],
        interval_seconds=3.0,
        timeout_seconds=2.0,
        window_size=10,
        outage_threshold=3,
    )

    monitor = NetworkMonitor(config, on_result=on_result)

    logging.info("Starting network monitor for %d hosts.", len(config.hosts))

    try:
        await monitor.start()

    finally:
        monitor.stop()
        database.close()
        logging.info("Network monitoring stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")