import streamlit as st



def _delta(
    current,
    previous,
    fmt="{:+.1f}"
):
    """
    Calculate change between two values.
    """

    if previous is None or current is None:
        return None


    difference = current - previous


    if difference == 0:
        return None


    return fmt.format(
        difference
    )




def render_summary(
    summary,
    previous_summary=None
):
    """
    Displays fleet-wide monitoring summary cards.
    """


    st.subheader(
        "Network Summary"
    )


    # ---------------------------------
    # Row 1
    # ---------------------------------

    col1, col2, col3, col4 = st.columns(4)



    with col1:

        st.metric(
            "Hosts",
            summary.get(
                "hosts_monitored",
                0
            ),
            delta=_delta(
                summary.get("hosts_monitored"),
                previous_summary.get("hosts_monitored")
                if previous_summary
                else None,
                "{:+d}"
            )
        )



    with col2:

        st.metric(
            "Total Checks",
            summary.get(
                "total_pings",
                0
            ),
            delta=_delta(
                summary.get("total_pings"),
                previous_summary.get("total_pings")
                if previous_summary
                else None,
                "{:+d}"
            )
        )



    with col3:

        uptime = summary.get(
            "fleet_uptime_pct",
            0
        )


        st.metric(
            "Fleet Uptime",
            f"{uptime}%",

            delta=_delta(
                uptime,
                previous_summary.get("fleet_uptime_pct")
                if previous_summary
                else None,
                "{:+.2f} pp"
            )
        )



    with col4:

        st.metric(
            "Total Outages",
            summary.get(
                "total_outages",
                0
            ),

            delta=_delta(
                summary.get("total_outages"),
                previous_summary.get("total_outages")
                if previous_summary
                else None,
                "{:+d}"
            ),

            delta_color="inverse"
        )



    # ---------------------------------
    # Row 2
    # ---------------------------------

    col1, col2, col3, col4 = st.columns(4)



    with col1:

        latency = summary.get(
            "fleet_avg_latency_ms"
        )


        st.metric(
            "Average Latency",

            (
                f"{latency} ms"
                if latency is not None
                else "N/A"
            ),

            delta=_delta(
                latency,
                previous_summary.get(
                    "fleet_avg_latency_ms"
                )
                if previous_summary
                else None,
                "{:+.1f} ms"
            ),

            delta_color="inverse"
        )



    with col2:

        st.metric(
            "Best Host",
            summary.get(
                "best_host"
            )
            or "None"
        )



    with col3:

        st.metric(
            "Worst Host",
            summary.get(
                "worst_host"
            )
            or "None"
        )



    with col4:

        down_hosts = summary.get(
            "currently_down_hosts",
            []
        )


        st.metric(
            "Hosts Down",
            len(
                down_hosts
            )
        )



    # ---------------------------------
    # Status Banner
    # ---------------------------------

    st.divider()


    currently_down = summary.get(
        "currently_down_hosts",
        []
    )


    if currently_down:

        st.error(
            "🔴 Hosts currently down: "
            +
            ", ".join(
                currently_down
            )
        )


    else:

        st.success(
            "🟢 All monitored hosts are reachable."
        )