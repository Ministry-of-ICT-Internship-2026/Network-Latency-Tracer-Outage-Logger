import streamlit as st

from dashboard.components.data import get_report
from dashboard.components.sidebar import render_sidebar


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Network Latency Monitoring",
    page_icon="🌐",
    layout="wide",
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

live_mode, refresh_interval = render_sidebar()


# --------------------------------------------------
# Load Report
# --------------------------------------------------

try:

    report = get_report()

except Exception as e:

    st.error(
        f"Unable to load monitoring data: {e}"
    )

    st.stop()



summary = report["summary"]



# --------------------------------------------------
# Home Page
# --------------------------------------------------

st.title(
    "🌐 Network Latency Monitoring System"
)


st.divider()



# --------------------------------------------------
# System Overview
# --------------------------------------------------

st.subheader(
    "System Overview"
)



col1, col2, col3, col4 = st.columns(4)



col1.metric(
    "Hosts Monitored",
    summary["hosts_monitored"]
)


col2.metric(
    "Total Checks",
    summary["total_pings"]
)


col3.metric(
    "Fleet Uptime",
    f"{summary['fleet_uptime_pct']}%"
)


col4.metric(
    "Total Outages",
    summary["total_outages"]
)



st.divider()



# --------------------------------------------------
# Navigation Guide
# --------------------------------------------------

st.subheader(
    "Dashboard Sections"
)



sections = [
    (
        "🌐 Dashboard",
        "Overall network performance, latency comparison, and fleet statistics."
    ),

    (
        "📡 Hosts",
        "Individual host monitoring, latency trends, and reliability details."
    ),

    (
        "🚨 Outages",
        "View outage events, downtime, and recovery history."
    ),

    (
        "📄 Reports",
        "Export CSV files and generate PDF reports."
    ),
]



cols = st.columns(4)



for col, (title, description) in zip(cols, sections):

    with col:

        st.info(
            f"""
            {title}

            {description}
            """
        )



st.divider()



# --------------------------------------------------
# Current Status
# --------------------------------------------------

st.subheader(
    "Current Network Status"
)



if summary["currently_down_hosts"]:

    st.error(
        "🔴 Hosts currently unavailable:\n\n"
        +
        ", ".join(
            summary["currently_down_hosts"]
        )
    )


else:

    st.success(
        "🟢 All monitored hosts are reachable."
    )