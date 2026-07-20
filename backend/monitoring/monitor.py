import asyncio
import logging

from typing import Callable, Dict, Optional

from monitoring.config import (
    MonitorConfig,
    load_targets_from_database
)

from monitoring.models import (
    HostStatus,
    PingResult
)

from monitoring.ping_engine import PingEngine


logger = logging.getLogger(__name__)



class NetworkMonitor:


    def __init__(
        self,
        config: MonitorConfig,
        on_result: Optional[
            Callable[[PingResult, HostStatus], None]
        ] = None,
    ):


        self.config = config


        self.targets = list(config.targets)


        self.engine = PingEngine(
            timeout=config.timeout_seconds
        )


        self.statuses: Dict[str, HostStatus] = {}


        self._sequence_counters: Dict[str, int] = {}


        self.on_result = on_result


        self._running = False


        # Add initial hosts

        for target in self.targets:

            self._add_host(target)




    # -------------------------------------
    # Add a new host dynamically
    # -------------------------------------

    def _add_host(self, target):

        if target.host in self.statuses:
            return

        logger.info(
            "Adding host to monitor: %s (%s)",
            target.name,
            target.host
        )

    # DO NOT append to self.targets here

        self.statuses[target.host] = HostStatus(
            host=target.host,
            window_size=self.config.window_size,
            outage_threshold=self.config.outage_threshold
        )

        self._sequence_counters[target.host] = 0




    # -------------------------------------
    # Check database for new hosts
    # -------------------------------------

    async def refresh_hosts(self):

        while self._running:

            try:

                database_targets = load_targets_from_database()


                for target in database_targets:


                    if target.host not in self.statuses:


                        logger.info(
                            "New host detected: %s",
                            target.host
                        )


                        # Add host to internal tracking
                        self._add_host(target)


                        # Keep target list updated
                        self.targets.append(target)


                        # Start latency monitoring immediately
                        asyncio.create_task(
                            self._monitor_host(
                                target.host
                            )
                        )


            except Exception as e:

                logger.error(
                    "Host refresh failed: %s",
                    e
                )


            await asyncio.sleep(5)



    # -------------------------------------
    # Monitor individual host
    # -------------------------------------

    async def _monitor_host(
        self,
        host: str
    ):


        status = self.statuses[host]


        while self._running:


            sequence = (
                self._sequence_counters[host]
            )


            self._sequence_counters[host] += 1



            result = await self.engine.probe(
                host,
                sequence
            )



            status.record(
                result
            )



            if self.on_result:

                self.on_result(
                    result,
                    status
                )



            await asyncio.sleep(
                self.config.interval_seconds
            )




    # -------------------------------------
    # Start monitoring
    # -------------------------------------

    async def start(self):


        self._running = True



        tasks = []


        for target in self.targets:


            tasks.append(

                asyncio.create_task(

                    self._monitor_host(
                        target.host
                    )

                )

            )



        # background database watcher

        tasks.append(

            asyncio.create_task(

                self.refresh_hosts()

            )

        )



        await asyncio.gather(
            *tasks
        )




    # -------------------------------------

    def stop(self):

        self._running = False




    def get_status(
        self,
        host: str
    ) -> HostStatus:

        return self.statuses[host]




    def get_all_statuses(self):

        return {

            host: status.summary()

            for host, status in self.statuses.items()

        }




    def get_target_name(
        self,
        host: str
    ) -> str:


        for target in self.targets:

            if target.host == host:

                return target.name


        return host