import logging
from datetime import datetime
from typing import Dict, Optional

from server.models import HostStatus, PingResult, OutageEvent

logger = logging.getLogger(__name__)

from server.config import config

threshold = config.outage_threshold


class OutageManager:
    """
    Detects outages based on consecutive ping failures.

    A host enters an outage when HostStatus.is_outage becomes True.

    When the host later recovers, an OutageEvent is created and
    returned so another module (such as database.py) can store it.
    """

    def __init__(self):
        # Keeps track of currently active outages.
        # Key = host
        # Value = outage start time
        self.active_outages: Dict[str, datetime] = {}

    def process(
        self,
        result: PingResult,
        status: HostStatus
    ) -> Optional[OutageEvent]:
        """
        Process the latest ping result.

        Returns:
            OutageEvent when an outage has completed.
            None otherwise.
        """

        host = result.host

        # -----------------------------
        # Host has entered an outage
        # -----------------------------
        if status.is_outage:

            if host not in self.active_outages:

                self.active_outages[host] = result.timestamp

                logger.warning(
                    "Outage started for %s at %s",
                    host,
                    result.timestamp,
                )

            return None

        # -----------------------------
        # Host has recovered
        # -----------------------------
        if host in self.active_outages:

            start_time = self.active_outages.pop(host)
            end_time = result.timestamp

            duration = (
                end_time - start_time
            ).total_seconds()

            outage = OutageEvent(
                host=host,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                reason="Consecutive ping failures",
            )

            logger.info(
                "Outage recovered for %s (%.2f seconds)",
                host,
                duration,
            )

            return outage

        return None