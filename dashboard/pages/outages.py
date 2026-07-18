import streamlit as st
import pandas as pd


from dashboard.components.data import get_report
from dashboard.components.tables import render_outage_table



st.set_page_config(
    page_title="Outages",
    page_icon="🚨",
    layout="wide"
)



st.title(
    "🚨 Network Outage Monitoring"
)



report = get_report()


summary = report["summary"]
outages = report["outage_log"]



# ---------------------------------
# Outage Summary
# ---------------------------------

st.subheader(
    "Outage Summary"
)


col1, col2, col3, col4 = st.columns(4)



with col1:

    st.metric(
        "Total Outages",
        summary["total_outages"]
    )



with col2:

    st.metric(
        "Downtime",
        summary["total_downtime_human"]
    )



with col3:

    st.metric(
        "Affected Hosts",
        len(
            set(
                o["host"]
                for o in outages
            )
        )
        if outages
        else 0
    )



with col4:

    active = [
        o for o in outages
        if o["end_time"] is None
    ]


    st.metric(
        "Active Outages",
        len(active)
    )



st.divider()



# ---------------------------------
# Current outages
# ---------------------------------

st.subheader(
    "Current Status"
)


active_outages = [
    outage
    for outage in outages
    if outage["end_time"] is None
]


if active_outages:

    st.error(
        "🔴 Some hosts are currently experiencing outages."
    )


    active_df = pd.DataFrame(
        active_outages
    )


    active_df = active_df[
        [
            "host",
            "start_time",
            "duration_seconds"
        ]
    ]


    active_df = active_df.rename(
        columns={
            "host": "Host",
            "start_time": "Started",
            "duration_seconds": "Duration (seconds)"
        }
    )


    st.dataframe(
        active_df,
        hide_index=True,
        width="stretch"
    )


else:

    st.success(
        "🟢 No active outages detected."
    )



st.divider()



# ---------------------------------
# Historical outage log
# ---------------------------------

render_outage_table(
    outages
)