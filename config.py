"""
config.py
---------
Central configuration for the Network Latency Tracer & Outage Logger.
Edit the values below to match your environment — no need to touch
any other file.
"""

# ---------------------------------------------------------------
# TARGETS TO MONITOR
# Each target has a friendly name and a host (IP address or hostname).
# Add as many as you like — e.g. gateway, DNS server, ISP uplink,
# a remote government server, etc.
# ---------------------------------------------------------------
TARGETS = [
    {"name": "Default Gateway", "host": "192.168.1.1"},
    {"name": "Google DNS", "host": "8.8.8.8"},
    {"name": "Cloudflare DNS", "host": "1.1.1.1"},
    # {"name": "Ministry HQ Server", "host": "10.0.0.5"},
]

# ---------------------------------------------------------------
# TIMING
# ---------------------------------------------------------------
PING_INTERVAL_SECONDS = 5        # how often each target is pinged
PING_TIMEOUT_SECONDS = 2         # how long to wait before counting as a timeout

# ---------------------------------------------------------------
# THRESHOLDS
# ---------------------------------------------------------------
DEGRADED_LATENCY_MS = 150        # above this = "degraded" status
CONSECUTIVE_FAILS_FOR_OUTAGE = 2 # how many consecutive timeouts before
                                  # we officially declare an "outage"
                                  # (avoids logging single dropped packets)

# ---------------------------------------------------------------
# SLA TARGETS
# ---------------------------------------------------------------
SLA_UPTIME_TARGET_PERCENT = 99.5   # required uptime % per SLA agreement

# ---------------------------------------------------------------
# OUTAGE SEVERITY
# ---------------------------------------------------------------
MAJOR_OUTAGE_SECONDS = 300   # outage >= this duration is "major", else "minor"

# ---------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------
DB_PATH = "network_logs.db"
