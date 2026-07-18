import time
from datetime import datetime

import streamlit as st
from server.config import config

INTERVAL_OPTIONS = {
    "5s": 5,
    "10s": 10,
    "30s": 30,
    "60s": 60,
    "5m": 300,
}


def render_sidebar():
    """
    Render sidebar controls for live monitoring.

    Returns:
        live_mode (bool)
        refresh_interval (int)
    """

    with st.sidebar:

        st.subheader("🔴 Live Monitoring")


        live_mode = st.toggle(
            "Enable auto-refresh",
            value=False
        )


        labels = list(INTERVAL_OPTIONS.keys())
        values = list(INTERVAL_OPTIONS.values())

        default_index = values.index(config.dashboard_refresh_seconds)

        interval_label = st.selectbox(
              "Refresh interval",
                 labels,
                 index=default_index,
                 disabled=not live_mode,
        )


        refresh_interval = INTERVAL_OPTIONS[
            interval_label
        ]


        # -----------------------------
        # Last refresh information
        # -----------------------------

        if "last_fetch_time" not in st.session_state:
            st.session_state.last_fetch_time = time.time()


        last_updated = datetime.fromtimestamp(
            st.session_state.last_fetch_time
        ).strftime("%H:%M:%S")


        if live_mode:

            remaining = max(
                0,
                int(
                    refresh_interval -
                    (
                        time.time()
                        -
                        st.session_state.last_fetch_time
                    )
                )
            )


            st.caption(
                f"🟢 Live — updated {last_updated} "
                f"· next refresh ~{remaining}s"
            )


        else:

            st.caption(
                f"⚪ Static — updated {last_updated}"
            )


    return live_mode, refresh_interval