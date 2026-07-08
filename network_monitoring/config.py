"""
Configuration for the network monitoring module.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class MonitorConfig:
    hosts: List[str]
    interval_seconds: float = 5.0    # time between probes, per host
    timeout_seconds: float = 2.0     # per-probe timeout before counting as a failure
    window_size: int = 10            # rolling window size for loss-rate / jitter stats
    outage_threshold: int = 3        # consecutive failures before a host is flagged as an outage
