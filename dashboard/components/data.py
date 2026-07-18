import streamlit as st

from server.analytics import MonitoringAnalytics



@st.cache_resource
def get_analytics() -> MonitoringAnalytics:
    """
    Creates and caches the analytics database connection.

    Cached because Streamlit reruns the script frequently,
    but we do not want to reopen the database every time.
    """

    return MonitoringAnalytics()



@st.cache_data(ttl=5)
def get_report():
    analytics = get_analytics()
    return analytics.build_full_report()