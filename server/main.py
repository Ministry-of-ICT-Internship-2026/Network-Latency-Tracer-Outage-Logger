import asyncio
import logging

from server.config import (
    MonitorConfig,
    load_targets_from_database
)

from server.models import (
    HostStatus,
    PingResult
)

from server.monitor import NetworkMonitor
from server.outage import OutageManager
from server.database import DatabaseManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)



database = DatabaseManager()

outage_manager = OutageManager()



# --------------------------------------------------
# Handle every ping result
# --------------------------------------------------

def on_result(
    result: PingResult,
    status: HostStatus
):

    # Save ping
    database.save_ping(result)



    # Check outage
    outage = outage_manager.process(
        result,
        status
    )


    if outage:

        database.save_outage(
            outage
        )


        logging.warning(
            "OUTAGE RECORDED | %s | %.2fs",
            outage.host,
            outage.duration_seconds
        )



    # Console output

    if result.success:

        message = (
            f"{result.rtt_ms:.2f} ms"
        )

    else:

        message = (
            f"FAILED ({result.error_type})"
        )



    print(
        f"[{result.host}] "
        f"seq={result.sequence} "
        f"{message} | "
        f"loss={status.loss_rate:.1f}% "
        f"avg={status.avg_rtt} "
        f"outage={status.is_outage}"
    )




# --------------------------------------------------
# Start monitoring
# --------------------------------------------------

async def main():

    targets = load_targets_from_database()



    if not targets:

        logging.warning(
            "No hosts found in database."
        )

        return



    config = MonitorConfig(

        targets=targets,

        interval_seconds=3,

        timeout_seconds=2,

        window_size=10,

        outage_threshold=3

    )



    monitor = NetworkMonitor(

        config,

        on_result

    )



    logging.info(
        "Starting monitor for %d hosts",
        len(targets)
    )



    for target in targets:

        logging.info(
            "Monitoring %s (%s)",
            target.name,
            target.host
        )



    try:

        await monitor.start()



    except asyncio.CancelledError:

        logging.info(
            "Monitor stopped"
        )



    finally:

        monitor.stop()

        database.close()



# --------------------------------------------------
# Program entry
# --------------------------------------------------

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )


    except KeyboardInterrupt:

        print(
            "\nShutdown requested."
        )