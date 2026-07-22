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


        self._monitor_tasks: Dict[str, asyncio.Task] = {}


        self.on_result = on_result


        self._running = False



        # Add initial hosts

        for target in self.targets:

            self._add_host(target)





    # -------------------------------------
    # Add host state
    # -------------------------------------

    def _add_host(self, target):


        if target.host in self.statuses:

            return



        logger.info(
            "Adding host to monitor: %s (%s)",
            target.name,
            target.host
        )



        self.statuses[target.host] = HostStatus(

            host=target.host,

            window_size=self.config.window_size,

            outage_threshold=self.config.outage_threshold

        )



        self._sequence_counters[target.host] = 0





    # -------------------------------------
    # Immediately start monitoring new host
    # -------------------------------------

    async def add_host_now(self, target):


        if target.host in self.statuses:

            return



        logger.info(
            "Immediately adding host: %s",
            target.host
        )



        self._add_host(target)



        self.targets.append(target)



        task = asyncio.create_task(

            self._monitor_host(
                target.host
            )

        )


        self._monitor_tasks[target.host] = task





    # -------------------------------------
    # Database watcher
    # -------------------------------------

    async def refresh_hosts(self):


        while self._running:


            try:


                database_targets = load_targets_from_database()



                active_hosts = {

                    target.host

                    for target in database_targets

                }




                # Add new hosts

                for target in database_targets:


                    if target.host not in self.statuses:


                        logger.info(
                            "New host detected: %s",
                            target.host
                        )


                        await self.add_host_now(
                            target
                        )





                # Remove disabled hosts

                for host in list(self.statuses.keys()):


                    if host not in active_hosts:


                        logger.info(
                            "Stopping monitoring for %s",
                            host
                        )



                        task = self._monitor_tasks.get(host)


                        if task:

                            task.cancel()



                        self.statuses.pop(
                            host,
                            None
                        )


                        self._sequence_counters.pop(
                            host,
                            None
                        )


                        self._monitor_tasks.pop(
                            host,
                            None
                        )



            except Exception as e:


                logger.error(
                    "Host refresh failed: %s",
                    e
                )



            await asyncio.sleep(1)





    # -------------------------------------
    # Monitor individual host
    # -------------------------------------

    async def _monitor_host(
        self,
        host: str
    ):


        logger.info(
            "Monitoring started for %s",
            host
        )



        status = self.statuses[host]



        while self._running:



            sequence = self._sequence_counters[host]



            self._sequence_counters[host] += 1




            result = await self.engine.probe(

                host,

                sequence

            )



            logger.info(

                "%s -> success=%s latency=%s",

                host,

                result.success,

                result.rtt_ms

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


            task = asyncio.create_task(

                self._monitor_host(

                    target.host

                )

            )


            self._monitor_tasks[target.host] = task


            tasks.append(task)





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