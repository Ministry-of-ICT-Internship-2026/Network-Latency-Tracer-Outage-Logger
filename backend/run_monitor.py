import logging

from monitoring.monitor import NetworkMonitor
from monitoring.config import (
    config,
    load_targets_from_database
)

from monitoring.database import DatabaseManager


logging.basicConfig(
    level=logging.INFO
)


db = DatabaseManager()



def handle_result(result, status):

    db.save_ping(result)

    logging.info(
        "Saved latency: %s -> %s ms",
        result.host,
        result.rtt_ms
    )



async def start_monitor():

    config.targets = load_targets_from_database()


    monitor = NetworkMonitor(
        config,
        on_result=handle_result
    )


    await monitor.start()