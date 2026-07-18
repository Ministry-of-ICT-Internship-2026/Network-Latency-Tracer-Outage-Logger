import streamlit as st

from dashboard.components.data import get_analytics
from dashboard.components.exports import render_exports


st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)



st.title(
    "📄 Network Reports"
)



st.write(
    """
    Generate and download monitoring reports.

    Available exports:

    - 📡 Latency measurements
    - 🚨 Outage history
    - 📊 Monitoring summary
    - 📄 Complete PDF report
    """
)



st.divider()



try:

    analytics = get_analytics()

except Exception as e:

    st.error(
        f"Unable to load analytics: {e}"
    )

    st.stop()



render_exports(
    analytics
)