import asyncio
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

    # save every ping
    db.save_ping(result)


    logging.info(
        "Saved latency: %s -> %s ms",
        result.host,
        result.rtt_ms
    )



async def main():

    config.targets = load_targets_from_database()


    monitor = NetworkMonitor(
        config,
        on_result=handle_result
    )


    await monitor.start()



if __name__ == "__main__":

    asyncio.run(main())