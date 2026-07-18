import pandas as pd
import plotly.express as px
import streamlit as st



def render_fleet_comparison(hosts):
    """
    Creates fleet-wide comparison charts.
    """

    if not hosts:
        return None, None


    data = []


    for host_id, host in hosts.items():

        data.append(
            {
                "Host": host.get(
                    "name",
                    host_id
                ),

                "Uptime (%)": host.get(
                    "uptime_pct",
                    0
                ),

                "Latency (ms)": host.get(
                    "avg_latency_ms"
                )
                or 0,

            }
        )


    df = pd.DataFrame(data)


    uptime_chart = px.bar(
        df,
        x="Host",
        y="Uptime (%)",
        title="Host Availability"
    )


    latency_chart = px.bar(
        df,
        x="Host",
        y="Latency (ms)",
        title="Average Latency"
    )


    return uptime_chart, latency_chart




def render_fleet_table(hosts):
    """
    Displays all monitored hosts.
    """


    if not hosts:

        st.info(
            "No hosts available."
        )

        return



    rows = []


    for host_id, host in hosts.items():

        rows.append(
            {
                "Host": host.get(
                    "name",
                    host_id
                ),

                "IP Address": host.get(
                    "host",
                    host_id
                ),

                "Status":
                    "🔴 Down"
                    if host.get("currently_down")
                    else "🟢 Online",


                "Uptime":
                    f"{host.get('uptime_pct',0)}%",


                "Average Latency":
                    (
                        f"{host.get('avg_latency_ms')} ms"
                        if host.get("avg_latency_ms")
                        else "N/A"
                    ),


                "Outages":
                    host.get(
                        "outage_count",
                        0
                    ),

                "Reliability":
                    host.get(
                        "reliability_grade",
                        "N/A"
                    )

            }
        )


    df = pd.DataFrame(rows)


    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )