"""
Outage detection module.

Monitors HostStatus objects and detects when hosts enter or recover
from an outage.

This module does not perform any database operations. Instead, it
returns completed OutageEvent objects which can be stored by the
database module.
"""

import logging
from typing import Dict, List, Optional

from models import HostStatus, PingResult, OutageEvent

logger = logging.getLogger(__name__)


class OutageManager:
    """
    Detects outages based on HostStatus.

    A host enters an outage when HostStatus.is_outage becomes True.

    A completed OutageEvent is returned only after the host has
    recovered.
    """

    def __init__(self):
        # Tracks which hosts are currently in an outage.
        self._active_outages: Dict[str, OutageEvent] = {}

    def process(
        self,
        result: PingResult,
        status: HostStatus
    ) -> Optional[OutageEvent]:
        """
        Processes the latest monitoring result.

        Returns:
            OutageEvent
                When an outage has completed.

            None
                If nothing significant happened.
        """

        host = result.host

        # -------------------------------------------------
        # Host has entered an outage
        # -------------------------------------------------
        if status.is_outage:

            if host not in self._active_outages:

                logger.warning(
                    "Outage detected for host %s",
                    host
                )

                self._active_outages[host] = OutageEvent(
                    host=host,
                    start_time=status.first_failure_time,
                    end_time=status.first_failure_time,
                    duration_seconds=0
                )

            return None

        # -------------------------------------------------
        # Host has recovered
        # -------------------------------------------------
        if host in self._active_outages:

            outage = self._active_outages.pop(host)

            outage.end_time = result.timestamp

            outage.duration_seconds = (
                outage.end_time - outage.start_time
            ).total_seconds()

            logger.info(
                "Host %s recovered after %.2f seconds",
                host,
                outage.duration_seconds
            )

            return outage

        return None

    def has_active_outage(self, host: str) -> bool:
        """
        Returns True if the specified host is currently in an outage.
        """

        return host in self._active_outages

    def get_active_outage(self, host: str) -> Optional[OutageEvent]:
        """
        Returns the active outage for a host.
        """

        return self._active_outages.get(host)

    def get_active_outages(self) -> List[OutageEvent]:
        """
        Returns all currently active outages.
        """

        return list(self._active_outages.values())

    def clear(self) -> None:
        """
        Clears all active outage tracking.

        Primarily intended for testing.
        """

        self._active_outages.clear()