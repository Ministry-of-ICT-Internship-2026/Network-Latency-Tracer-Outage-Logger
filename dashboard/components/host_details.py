import streamlit as st
import pandas as pd

from dashboard.components.charts import (
    render_latency_chart,
    render_loss_chart,
)


GRADE_BADGE = {
    "Excellent": "🟢",
    "Good": "🟢",
    "Fair": "🟡",
    "Poor": "🟠",
    "Critical": "🔴",
    "N/A": "⚪",
}



def _human_duration(total_seconds):
    """
    Convert seconds into readable duration.
    """

    if not total_seconds:
        return "0s"

    seconds = int(total_seconds)

    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)




def render_host_details(
    hosts,
    summary,
):
    """
    Display detailed monitoring information
    for a selected host.
    """


    st.subheader(
        "Host Detail"
    )


    if not hosts:

        st.info(
            "No hosts have reported data yet."
        )

        return



    host_name = st.selectbox(
        "Select a host",
        sorted(hosts.keys())
    )


    host = hosts[host_name]


    badge = GRADE_BADGE.get(
        host.get("reliability_grade"),
        "⚪"
    )


    title = (
        f"### {badge} "
        f"{host_name} — "
        f"{host.get('reliability_grade','N/A')}"
    )


    if host.get("currently_down"):

        title += " 🔴 currently down"


    st.markdown(title)



    overview, latency, loss, outages = st.tabs(
        [
            "📊 Overview",
            "📈 Latency",
            "📉 Loss & Errors",
            "🕳️ Outages",
        ]
    )



    # ==============================
    # Overview
    # ==============================

    with overview:


        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "Uptime",
            f"{host.get('uptime_pct',0)}%"
        )


        latency_value = host.get(
            "avg_latency_ms"
        )


        c2.metric(
            "Average Latency",
            (
                f"{latency_value} ms"
                if latency_value is not None
                else "N/A"
            )
        )


        p95 = host.get(
            "p95_latency_ms"
        )


        c3.metric(
            "P95 Latency",
            (
                f"{p95} ms"
                if p95 is not None
                else "N/A"
            )
        )


        c4.metric(
            "Outages",
            host.get(
                "outage_count",
                0
            )
        )



        st.divider()



        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "Total Pings",
            host.get(
                "total_pings",
                0
            )
        )


        c2.metric(
            "Failed Pings",
            host.get(
                "failed_pings",
                0
            )
        )


        c3.metric(
            "Downtime",
            _human_duration(
                host.get(
                    "total_downtime_seconds",
                    0
                )
            )
        )


        longest = host.get(
            "longest_outage_seconds"
        )


        c4.metric(
            "Longest Outage",
            (
                f"{longest:.0f}s"
                if longest
                else "None"
            )
        )



        st.divider()


        st.markdown(
            "**Comparison with fleet average**"
        )


        fleet_latency = summary.get(
            "fleet_avg_latency_ms"
        )


        fleet_uptime = summary.get(
            "fleet_uptime_pct"
        )


        col1, col2 = st.columns(2)



        with col1:

            if (
                latency_value is not None
                and fleet_latency is not None
            ):

                diff = (
                    latency_value
                    - fleet_latency
                )

                st.metric(
                    "Latency difference",
                    f"{latency_value} ms",
                    delta=f"{diff:+.1f} ms"
                )



        with col2:

            if fleet_uptime is not None:

                diff = (
                    host["uptime_pct"]
                    - fleet_uptime
                )


                st.metric(
                    "Uptime difference",
                    f"{host['uptime_pct']}%",
                    delta=f"{diff:+.2f}%"
                )




    # ==============================
    # Latency
    # ==============================

    with latency:

        fig = render_latency_chart(
            host
        )


        if fig:

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "No latency data available."
            )



    # ==============================
    # Loss & Errors
    # ==============================

    with loss:


        fig = render_loss_chart(
            host
        )


        if fig:

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "No packet loss data available."
            )



        st.divider()


        errors = host.get(
            "error_breakdown",
            {}
        )


        if errors:

            df = pd.DataFrame(
                list(errors.items()),
                columns=[
                    "Error Type",
                    "Count"
                ]
            )


            st.dataframe(
                df,
                hide_index=True,
                width="stretch"
            )

        else:

            st.success(
                "No errors recorded."
            )



    # ==============================
    # Outages
    # ==============================

    with outages:


        outage_list = host.get(
            "outages",
            []
        )


        if outage_list:


            df = pd.DataFrame(
                outage_list
            )


            df["end_time"] = (
                df["end_time"]
                .fillna("Ongoing")
            )


            df = df[
                [
                    "start_time",
                    "end_time",
                    "duration_seconds",
                ]
            ]


            st.dataframe(
                df,
                hide_index=True,
                width="stretch"
            )


        else:

            st.success(
                "No outages recorded."
            )