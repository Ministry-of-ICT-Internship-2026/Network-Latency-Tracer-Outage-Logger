import streamlit as st

from dashboard.components.data import get_report
from dashboard.components.host_details import render_host_details
from dashboard.components.tables import render_fleet_table


st.set_page_config(
    page_title="Hosts",
    page_icon="📡",
    layout="wide"
)


st.title(
    "📡 Host Monitoring"
)


report = get_report()


hosts = report["hosts"]
summary = report["summary"]


# ---------------------------------
# Host overview table
# ---------------------------------

st.subheader(
    "Monitored Hosts"
)


render_fleet_table(
    hosts
)


st.divider()


# ---------------------------------
# Detailed host view
# ---------------------------------

render_host_details(
    hosts,
    summary,
)