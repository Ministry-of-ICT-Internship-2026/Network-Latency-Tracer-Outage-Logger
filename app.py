"""
app.py
------
Streamlit dashboard for the Network Latency Tracer & Outage Logger.

Run with:
    streamlit run app.py

This is a pure "viewer" - it never pings anything itself. All data
comes from the SQLite database that tracer.py fills in the
background. You can close/reopen this dashboard anytime without
losing any historical data.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import config
import db
import analytics


# =================================================================
# PAGE SETUP
# =================================================================
st.set_page_config(
    page_title="Network Latency Tracer",
    page_icon="📡",
    layout="wide",
)

db.init_db()  # safe no-op if tables already exist

st.title("📡 Network Latency Tracer & Outage Logger")
st.caption("Historical network performance monitoring for SLA enforcement")


# =================================================================
# SIDEBAR — FILTERS
# =================================================================
st.sidebar.header("Filters")

configured_targets = [t["name"] for t in config.TARGETS]
seen_targets = db.get_all_targets_seen()
all_targets = sorted(set(configured_targets) | set(seen_targets))

target_choice = st.sidebar.selectbox("Target", ["All"] + all_targets)

time_range_label = st.sidebar.selectbox(
    "Time range",
    ["Last hour", "Last 24 hours", "Last 7 days", "Last 30 days"],
    index=1,
)
hours_map = {
    "Last hour": 1,
    "Last 24 hours": 24,
    "Last 7 days": 24 * 7,
    "Last 30 days": 24 * 30,
}
hours = hours_map[time_range_label]

auto_refresh = st.sidebar.checkbox("Auto-refresh every 30s", value=False)
if auto_refresh:
    st.sidebar.caption("Dashboard will refresh automatically.")
    st.markdown(
        "<meta http-equiv='refresh' content='30'>", unsafe_allow_html=True
    )

if st.sidebar.button("🔄 Refresh now"):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption(
    f"SLA target: **{config.SLA_UPTIME_TARGET_PERCENT}%** uptime\n\n"
    f"Degraded above: **{config.DEGRADED_LATENCY_MS}ms**"
)


# =================================================================
# TOP KPI CARDS — one row per monitored target's live status
# =================================================================
st.subheader("Live Status")

display_targets = configured_targets if target_choice == "All" else [target_choice]

status_cols = st.columns(len(display_targets)) if display_targets else []
for col, t in zip(status_cols, display_targets):
    current = analytics.get_current_status(t)
    uptime = analytics.calculate_uptime_percentage(t, hours)

    status_icon = {"ok": "🟢", "degraded": "🟡", "timeout": "🔴", "unknown": "⚪"}.get(
        current["status"], "⚪"
    )
    latency_display = (
        f"{current['latency_ms']:.1f} ms" if current["latency_ms"] is not None else "—"
    )

    with col:
        st.metric(
            label=f"{status_icon} {t}",
            value=latency_display,
            delta=f"{uptime}% uptime ({time_range_label.lower()})",
            delta_color="off",
        )

st.divider()


# =================================================================
# LATENCY OVER TIME — main chart with outage overlay
# =================================================================
st.subheader("Latency Over Time")

df = analytics.get_ping_dataframe(target_choice if target_choice != "All" else display_targets[0] if display_targets else "All", hours) \
    if target_choice != "All" else pd.concat(
        [analytics.get_ping_dataframe(t, hours).assign(target=t) for t in display_targets],
        ignore_index=True,
    ) if display_targets else pd.DataFrame()

if df.empty:
    st.info("No ping data yet for this selection. Make sure tracer.py is running.")
else:
    fig = go.Figure()

    for t in df["target"].unique():
        sub = df[df["target"] == t]
        fig.add_trace(go.Scatter(
            x=sub["timestamp"],
            y=sub["latency_ms"],
            mode="lines+markers",
            name=t,
            connectgaps=False,
            marker=dict(size=4),
        ))

    # Overlay outage bands
    outage_targets = display_targets
    for t in outage_targets:
        outages_df = analytics.get_outages_df(t, hours)
        for _, o in outages_df.iterrows():
            end = o["end_time"] if pd.notna(o["end_time"]) else pd.Timestamp.now().isoformat()
            fig.add_vrect(
                x0=o["start_time"], x1=end,
                fillcolor="red", opacity=0.15, line_width=0,
            )

    fig.add_hline(
        y=config.DEGRADED_LATENCY_MS,
        line_dash="dot",
        line_color="orange",
        annotation_text="Degraded threshold",
        annotation_position="top left",
    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Latency (ms)",
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Shaded red bands indicate logged outage periods.")

st.divider()


# =================================================================
# OUTAGE LOG TABLE
# =================================================================
st.subheader("Outage Log")

outage_frames = []
for t in display_targets:
    d = analytics.get_outages_df(t, hours)
    if not d.empty:
        outage_frames.append(d)

if outage_frames:
    outages_all = pd.concat(outage_frames, ignore_index=True)
    outages_all = outages_all.sort_values("start_time", ascending=False)
    display_df = outages_all[["target", "start_time", "end_time", "duration_display", "severity"]]
    display_df.columns = ["Target", "Start", "End", "Duration", "Severity"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export outage log as CSV",
        data=csv,
        file_name="outage_log.csv",
        mime="text/csv",
    )
else:
    st.success("No outages logged in this time range. 🎉")

st.divider()


# =================================================================
# SLA COMPLIANCE
# =================================================================
st.subheader("SLA Compliance (last 30 days)")

sla_rows = []
for t in configured_targets:
    sla_rows.append(analytics.get_sla_compliance(t, hours=24 * 30))
sla_df = pd.DataFrame(sla_rows)

if not sla_df.empty:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=sla_df["target"], y=sla_df["actual_uptime"],
        name="Actual Uptime %",
        marker_color=["#2ecc71" if c else "#e74c3c" for c in sla_df["compliant"]],
    ))
    fig2.add_trace(go.Scatter(
        x=sla_df["target"], y=[config.SLA_UPTIME_TARGET_PERCENT] * len(sla_df),
        mode="lines", name="SLA Required %",
        line=dict(color="black", dash="dash"),
    ))
    fig2.update_layout(
        yaxis_title="Uptime %",
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)

    breaches = sla_df[~sla_df["compliant"]]
    if not breaches.empty:
        st.warning(
            f"⚠️ SLA breach on: {', '.join(breaches['target'].tolist())}"
        )
    else:
        st.success("✅ All targets are meeting their SLA uptime requirement.")

st.divider()


# =================================================================
# WORST OFFENDERS (multi-link ranking)
# =================================================================
if len(configured_targets) > 1:
    st.subheader("Worst Offenders (last 7 days)")
    offenders_df = analytics.get_worst_offenders(configured_targets, hours=24 * 7)
    if not offenders_df.empty:
        show_df = offenders_df[["target", "total_outages", "total_downtime_display", "uptime_pct"]]
        show_df.columns = ["Target", "Outages", "Total Downtime", "Uptime %"]
        st.dataframe(show_df, use_container_width=True, hide_index=True)
