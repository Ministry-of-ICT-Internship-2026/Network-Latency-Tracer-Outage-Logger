"""
Ping engine — sends ICMP echo requests in unprivileged mode and returns
structured results.

Built on icmplib using SOCK_DGRAM (unprivileged), not raw sockets. This
means no root/admin privileges are required, but on Linux it does depend
on the net.ipv4.ping_group_range sysctl permitting the running user's
group to open ICMP datagram sockets. That dependency is real and is
surfaced explicitly on failure rather than silently treated as "host down" -
a permission error and a dead host are different problems and should not
look identical in the logs.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from icmplib import async_ping, ICMPLibError, SocketPermissionError

from monitoring.models import PingResult

logger = logging.getLogger(__name__)


class PingEngine:
    """
    Thin async wrapper around icmplib, hardcoded to unprivileged mode.

    No privileged/raw-socket fallback by design: this module may run in
    contexts without guaranteed root/admin, so unprivileged mode is the
    only path, and its failure modes are handled explicitly rather than
    assumed away.
    """

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout

    async def probe(self, host: str, sequence: int) -> PingResult:
        sent_at = datetime.now(timezone.utc)

        try:
            result = await async_ping(
                address=host,
                count=1,
                timeout=self.timeout,
                privileged=False,  # unprivileged (SOCK_DGRAM) only
            )

            if result.is_alive:
                return PingResult(
                    host=host,
                    sequence=sequence,
                    timestamp=sent_at,
                    success=True,
                    rtt_ms=result.avg_rtt,
                    error_type=None,
                )

            return PingResult(
                host=host,
                sequence=sequence,
                timestamp=sent_at,
                success=False,
                rtt_ms=None,
                error_type="timeout",
            )

        except SocketPermissionError as exc:
            # Configuration problem, not a network condition. Logged loudly
            # and distinctly so it isn't mistaken for the host being down.
            logger.error(
                "Unprivileged ICMP socket denied for host %s: %s. "
                "On Linux, check `sysctl net.ipv4.ping_group_range` includes "
                "this process's group. This is a system permission issue.",
                host, exc,
            )
            return PingResult(
                host=host,
                sequence=sequence,
                timestamp=sent_at,
                success=False,
                rtt_ms=None,
                error_type="permission_denied",
            )

        except ICMPLibError as exc:
            # Covers name resolution failures, destination unreachable, etc.
            logger.warning("Ping to %s failed: %s", host, exc)
            return PingResult(
                host=host,
                sequence=sequence,
                timestamp=sent_at,
                success=False,
                rtt_ms=None,
                error_type="unreachable",
            )
