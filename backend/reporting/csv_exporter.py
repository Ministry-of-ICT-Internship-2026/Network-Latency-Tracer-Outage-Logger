import csv
from io import StringIO



def generate_csv(report):

    output = StringIO()

    writer = csv.writer(output)


    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================

    writer.writerow(
        [
            "Executive Summary"
        ]
    )


    writer.writerow(
        [
            "Metric",
            "Value"
        ]
    )


    summary = report.get(
        "summary",
        {}
    )


    for key, value in summary.items():

        writer.writerow(
            [
                key,
                value
            ]
        )


    writer.writerow([])



    # ==================================================
    # HOST RELIABILITY
    # ==================================================

    writer.writerow(
        [
            "Host Reliability"
        ]
    )


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


    for host, data in report.get(
        "hosts",
        {}
    ).items():


        writer.writerow(

            [

                data.get(
                    "name",
                    host
                ),

                host,


                (
                    "Down"
                    if data.get(
                        "currently_down"
                    )
                    else "Online"
                ),


                data.get(
                    "uptime_pct"
                ),


                data.get(
                    "avg_latency_ms"
                ),


                data.get(
                    "outage_count"
                ),


                data.get(
                    "total_downtime_seconds"
                ),


                data.get(
                    "reliability_grade"
                )

            ]

        )


    writer.writerow([])



    # ==================================================
    # OUTAGE HISTORY
    # ==================================================

    writer.writerow(
        [
            "Outage History"
        ]
    )


    writer.writerow(

        [
            "Host",
            "Start Time",
            "End Time",
            "Duration Seconds"
        ]

    )


    outage_log = report.get(
        "outage_log",
        []
    )


    for outage in outage_log:


        writer.writerow(

            [

                outage.get(
                    "host"
                ),

                outage.get(
                    "start_time"
                ),

                outage.get(
                    "end_time"
                ),

                outage.get(
                    "duration_seconds"
                )

            ]

        )



    return output.getvalue()