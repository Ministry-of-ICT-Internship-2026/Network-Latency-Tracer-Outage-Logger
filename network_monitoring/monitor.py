"""
Async orchestrator: runs one independent probing loop per host so a
dead/unreachable host never blocks or delays monitoring of the others.
"""
import asyncio
import logging
from typing import Callable, Dict, Optional

from config import MonitorConfig
from models import HostStatus, PingResult
from ping_engine import PingEngine

logger = logging.getLogger(__name__)


class NetworkMonitor:
    def __init__(
        self,
        config: MonitorConfig,
        on_result: Optional[Callable[[PingResult, HostStatus], None]] = None,
    ):
        self.config = config
        self.engine = PingEngine(timeout=config.timeout_seconds)
        self.statuses: Dict[str, HostStatus] = {
            host: HostStatus(host, config.window_size, config.outage_threshold)
            for host in config.hosts
        }
        self.on_result = on_result
        self._sequence_counters: Dict[str, int] = {host: 0 for host in config.hosts}
        self._running = False

    async def _monitor_host(self, host: str) -> None:
        status = self.statuses[host]
        while self._running:
            seq = self._sequence_counters[host]
            self._sequence_counters[host] += 1

            result = await self.engine.probe(host, seq)
            was_outage = status.is_outage
            status.record(result)

            if status.is_outage and not was_outage:
                logger.warning(
                    "OUTAGE detected for %s (%d consecutive failures)",
                    host, status.consecutive_failures,
                )
            elif was_outage and not status.is_outage:
                logger.info("Host %s recovered", host)

            if self.on_result:
                self.on_result(result, status)

            await asyncio.sleep(self.config.interval_seconds)

    async def start(self) -> None:
        """Runs indefinitely until stop() is called from another coroutine/task."""
        self._running = True
        tasks = [self._monitor_host(host) for host in self.config.hosts]
        await asyncio.gather(*tasks)

    def stop(self) -> None:
        self._running = False

    def get_status(self, host: str) -> HostStatus:
        return self.statuses[host]

    def get_all_statuses(self) -> Dict[str, dict]:
        return {host: status.summary() for host, status in self.statuses.items()}
