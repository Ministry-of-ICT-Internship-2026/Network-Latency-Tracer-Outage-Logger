import streamlit as st
import pandas as pd



def _format_duration(seconds):
    """
    Convert seconds into readable duration.
    """

    if not seconds:
        return "0s"


    seconds = int(seconds)

    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)


    parts = []


    if hours:
        parts.append(
            f"{hours}h"
        )

    if minutes:
        parts.append(
            f"{minutes}m"
        )

    if seconds:
        parts.append(
            f"{seconds}s"
        )


    return " ".join(parts)



# --------------------------------------------------
# Fleet Host Table
# --------------------------------------------------

def render_fleet_table(hosts):
    """
    Displays fleet-wide host comparison table.
    """


    st.subheader(
        "Host Overview"
    )


    if not hosts:

        st.info(
            "No hosts available."
        )

        return



    rows = []


    for host in hosts.values():

        rows.append(
            {
                "Host": host.get(
                    "host",
                    "Unknown"
                ),

                "Status": (
                    "🔴 Down"
                    if host.get("currently_down")
                    else "🟢 Online"
                ),

                "Uptime (%)": host.get(
                    "uptime_pct",
                    0
                ),

                "Latency (ms)": (
                    host["avg_latency_ms"]
                    if host["avg_latency_ms"] is not None
                    else 0
                ),

                "Grade": host.get(
                    "reliability_grade",
                    "N/A"
                ),

                "Outages": host.get(
                    "outage_count",
                    0
                ),
            }
        )


    df = pd.DataFrame(rows)


    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )



# --------------------------------------------------
# Error Table
# --------------------------------------------------

def render_error_table(error_breakdown):
    """
    Displays network error statistics.
    """


    st.subheader(
        "Error Breakdown"
    )


    if not error_breakdown:

        st.success(
            "No errors recorded."
        )

        return



    df = pd.DataFrame(
        list(error_breakdown.items()),
        columns=[
            "Error Type",
            "Count"
        ],
    )


    df = df.sort_values(
        "Count",
        ascending=False
    )


    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )



# --------------------------------------------------
# Outage Table
# --------------------------------------------------

def render_outage_table(outage_log):
    """
    Displays all outages across monitored hosts.
    """


    st.subheader(
        "🚨 Fleet Outage Log"
    )


    if not outage_log:

        st.info(
            "No outages recorded across the fleet."
        )

        return



    df = pd.DataFrame(
        outage_log
    )


    required_columns = [
        "host",
        "start_time",
        "end_time",
        "duration_seconds",
    ]


    df = df[
        required_columns
    ]


    df["end_time"] = (
        df["end_time"]
        .fillna("Ongoing")
    )


    df["duration_seconds"] = (
        df["duration_seconds"]
        .apply(_format_duration)
    )


    df = df.rename(
        columns={
            "host": "name",
            "start_time": "Start Time",
            "end_time": "End Time",
            "duration_seconds": "Duration",
        }
    )


    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )