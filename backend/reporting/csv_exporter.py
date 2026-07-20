import csv
from io import StringIO


def generate_csv(report):

    output = StringIO()


    writer = csv.writer(output)



    # Header

    writer.writerow(
        [
            "Host",
            "IP Address",
            "Status",
            "Uptime %",
            "Average Latency (ms)",
            "Outages",
            "Downtime (seconds)",
            "Reliability Grade"
        ]
    )



    for host, data in report["hosts"].items():


        writer.writerow(
            [
                data["name"],
                host,

                "Down"
                if data["currently_down"]
                else "Online",

                data["uptime_pct"],

                data["avg_latency_ms"],

                data["outage_count"],

                data["total_downtime_seconds"],

                data["reliability_grade"]
            ]
        )



    return output.getvalue()