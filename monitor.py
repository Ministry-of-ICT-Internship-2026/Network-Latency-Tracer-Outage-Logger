from ping3 import ping
from datetime import datetime
import time

HOST = "8.8.8.8"
TIMEOUT = 2
PING_INTERVAL = 5


def ping_host(host):
    """
    Ping a host and return the latency in milliseconds.
    Returns None if the host cannot be reached.
    """
    latency = ping(host, timeout=TIMEOUT)

    if latency is not None:
        latency *= 1000  # Convert seconds to milliseconds

    return latency

def create_record(host, latency):
    """
    Creates a monitoring record containing all relevant information.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if latency is None:
        status = "Offline"
    else:
        status = "Online"

    return {
        "timestamp": timestamp,
        "host": host,
        "latency": latency,
        "status": status
    }

def main():
    print("Network Monitor Started")
    print(f"Monitoring {HOST} every {PING_INTERVAL} seconds...")
    print("-" * 50)

    while True:
        latency = ping_host(HOST)

        record = create_record(HOST, latency)

        print("-" * 50)
        print(f"Time    : {record['timestamp']}")
        print(f"Host    : {record['host']}")
        print(f"Status  : {record['status']}")

        if record["latency"] is not None:
            print(f"Latency : {record['latency']:.2f} ms")
        else:
            print("Latency : N/A")

        # Wait before the next ping
        time.sleep(PING_INTERVAL)


if __name__ == "__main__":
    main()
