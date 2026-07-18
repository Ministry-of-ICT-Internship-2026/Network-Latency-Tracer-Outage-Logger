import streamlit as st

from dashboard.components.data import get_report
from dashboard.components.metrics import render_summary
from dashboard.components.fleet import (
    render_fleet_comparison,
    render_fleet_table
)
from streamlit_autorefresh import st_autorefresh

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="dashboard_refresh")


st.set_page_config(
    page_title="Network Dashboard",
    page_icon="🌐",
    layout="wide"
)


st.title(
    "🌐 Network Monitoring Dashboard"
)


report = get_report()


summary = report["summary"]
hosts = report["hosts"]


# -------------------------
# Summary cards
# -------------------------

render_summary(
    summary
)


st.divider()


# -------------------------
# Fleet comparison
# -------------------------

st.subheader(
    "Fleet Performance"
)


uptime_fig, latency_fig = render_fleet_comparison(
    hosts
)


col1, col2 = st.columns(2)


with col1:
    if uptime_fig:
        st.plotly_chart(
            uptime_fig,
            width="stretch"
        )
    else:
        st.info(
            "No uptime data available."
        )


with col2:
    if latency_fig:
        st.plotly_chart(
            latency_fig,
            width="stretch"
        )
    else:
        st.info(
            "No latency data available."
        )


st.divider()


# -------------------------
# Fleet Host Table
# -------------------------

st.subheader(
    "Host Status"
)


render_fleet_table(
    hosts
)