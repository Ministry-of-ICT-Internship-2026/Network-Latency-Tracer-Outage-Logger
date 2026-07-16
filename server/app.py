import time
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

from analytics import MonitoringAnalytics
from reports import ReportGenerator

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Network Latency Dashboard",
    page_icon="🌐",
    layout="wide",
)

st.title("🌐 Network Latency Monitoring Dashboard")
st.write("Real-time monitoring and analytics for monitored network hosts.")

GRADE_COLORS = {
    "Excellent": "#2ecc71",
    "Good": "#27ae60",
    "Fair": "#f1c40f",
    "Poor": "#e67e22",
    "Critical": "#e74c3c",
    "N/A": "#95a5a6",
}

GRADE_BADGE = {
    "Excellent": "🟢",
    "Good": "🟢",
    "Fair": "🟡",
    "Poor": "🟠",
    "Critical": "🔴",
    "N/A": "⚪",
}

# --------------------------------------------------
# Load Analytics (cached so we don't hit the DB on every widget interaction)
# --------------------------------------------------

@st.cache_resource
def get_analytics() -> MonitoringAnalytics:
    return MonitoringAnalytics()


@st.cache_data
def get_report():
    # analytics is a cached resource, safe to reuse across reruns.
    # No fixed ttl here - refresh timing is controlled manually below
    # so it lines up with the user's chosen live-polling interval.
    return get_analytics().build_full_report()


# --------------------------------------------------
# Live auto-refresh controls
# --------------------------------------------------

INTERVAL_OPTIONS = {"5s": 5, "10s": 10, "30s": 30, "60s": 60, "5m": 300}

with st.sidebar:
    st.subheader("🔴 Live Monitoring")
    live_mode = st.toggle("Enable auto-refresh", value=False)
    interval_label = st.selectbox(
        "Refresh interval",
        list(INTERVAL_OPTIONS.keys()),
        index=1,
        disabled=not live_mode,
    )
    refresh_interval = INTERVAL_OPTIONS[interval_label]

if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = 0.0

now = time.time()
seconds_since_fetch = now - st.session_state.last_fetch_time

if st.session_state.last_fetch_time == 0.0:
    st.session_state.last_fetch_time = now
elif live_mode and seconds_since_fetch >= refresh_interval:
    get_report.clear()
    st.session_state.last_fetch_time = now

# Drives the periodic rerun that lets the check above fire on a timer.
# Only active while live mode is on - a manual refresh or normal
# interaction doesn't need it.
if live_mode:
    st_autorefresh(interval=refresh_interval * 1000, key="live_autorefresh")

try:
    analytics = get_analytics()
    report = get_report()
except Exception as e:
    st.error(f"Unable to load analytics: {e}")
    st.stop()

period = report["period"]
summary = report["summary"]
hosts = report["hosts"]

with st.sidebar:
    last_updated = datetime.fromtimestamp(st.session_state.last_fetch_time).strftime("%H:%M:%S")
    if live_mode:
        next_in = max(0, int(refresh_interval - (time.time() - st.session_state.last_fetch_time)))
        st.caption(f"🟢 Live — last updated {last_updated} · next refresh in ~{next_in}s")
    else:
        st.caption(f"⚪ Static — last updated {last_updated}")

# --------------------------------------------------
# Trend tracking: keep the last two *distinct* fetches in session_state
# so metrics can show a delta since the previous poll, not just the
# current snapshot. New entries are only pushed when the underlying
# report actually changed (new generated_at), so repeated reruns from
# widget clicks within the cache TTL don't wipe out the comparison.
# --------------------------------------------------

if "report_history" not in st.session_state:
    st.session_state.report_history = []

history = st.session_state.report_history
if not history or history[0]["generated_at"] != report["generated_at"]:
    history.insert(0, report)
    del history[2:]

prev_report = history[1] if len(history) > 1 else None
prev_summary = prev_report["summary"] if prev_report else None
prev_hosts = prev_report["hosts"] if prev_report else None


def _human_duration(total_seconds):
    """Formats a duration in seconds as e.g. '2h 14m' for display."""
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


def _delta(curr, prev, fmt="{:+.1f}"):
    """Returns a formatted delta string, or None if no comparison is available."""
    if prev is None or curr is None:
        return None
    diff = curr - prev
    if abs(diff) < 1e-9:
        return None
    return fmt.format(diff)


if st.button("🔄 Refresh now"):
    get_report.clear()
    st.session_state.last_fetch_time = time.time()
    st.rerun()

# --------------------------------------------------
# Monitoring Information
# --------------------------------------------------

st.subheader("Monitoring Information")

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Monitoring Started:** {period['start']}")

with col2:
    st.write(f"**Monitoring Ended:** {period['end']}")

# --------------------------------------------------
# Fleet Summary
# --------------------------------------------------

st.subheader("Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Hosts",
        summary["hosts_monitored"],
        delta=_delta(summary["hosts_monitored"], prev_summary["hosts_monitored"] if prev_summary else None, "{:+d}"),
    )

with col2:
    st.metric(
        "Total Pings",
        summary["total_pings"],
        delta=_delta(summary["total_pings"], prev_summary["total_pings"] if prev_summary else None, "{:+d}"),
    )

with col3:
    st.metric(
        "Fleet Uptime",
        f"{summary['fleet_uptime_pct']}%",
        delta=_delta(
            summary["fleet_uptime_pct"],
            prev_summary["fleet_uptime_pct"] if prev_summary else None,
            "{:+.2f} pp",
        ),
    )

with col4:
    st.metric(
        "Total Outages",
        summary["total_outages"],
        delta=_delta(summary["total_outages"], prev_summary["total_outages"] if prev_summary else None, "{:+d}"),
        delta_color="inverse",
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Latency",
        f"{summary['fleet_avg_latency_ms']} ms",
        delta=_delta(
            summary["fleet_avg_latency_ms"],
            prev_summary["fleet_avg_latency_ms"] if prev_summary else None,
            "{:+.1f} ms",
        ),
        delta_color="inverse",
    )

with col2:
    st.metric("Worst Host", summary["worst_host"] or "None")

with col3:
    st.metric("Best Host", summary["best_host"] or "None")

if summary["currently_down_hosts"]:
    st.error(f"🔴 Currently down: {', '.join(summary['currently_down_hosts'])}")
else:
    st.success("🟢 All hosts currently reachable")

st.divider()

# --------------------------------------------------
# Fleet-wide Comparison Charts
# --------------------------------------------------

st.subheader("Fleet Comparison")

if hosts:
    fleet_df = pd.DataFrame(
        [
            {
                "Host": h["host"],
                "Uptime (%)": h["uptime_pct"],
                "Avg Latency (ms)": h["avg_latency_ms"] or 0,
                "Grade": h["reliability_grade"],
                "Outages": h["outage_count"],
            }
            for h in hosts.values()
        ]
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        uptime_fig = px.bar(
            fleet_df.sort_values("Uptime (%)"),
            x="Uptime (%)",
            y="Host",
            orientation="h",
            color="Grade",
            color_discrete_map=GRADE_COLORS,
            text="Uptime (%)",
            title="Uptime by Host",
        )
        uptime_fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        uptime_fig.update_layout(
            xaxis_range=[max(0, fleet_df["Uptime (%)"].min() - 5), 100],
            showlegend=True,
            height=max(300, 40 * len(fleet_df)),
        )
        st.plotly_chart(uptime_fig, use_container_width=True)

    with chart_col2:
        latency_fig = px.bar(
            fleet_df.sort_values("Avg Latency (ms)", ascending=False),
            x="Avg Latency (ms)",
            y="Host",
            orientation="h",
            color="Avg Latency (ms)",
            color_continuous_scale="Blues",
            text="Avg Latency (ms)",
            title="Average Latency by Host",
        )
        latency_fig.update_traces(texttemplate="%{text:.1f} ms", textposition="outside")
        latency_fig.update_layout(height=max(300, 40 * len(fleet_df)), coloraxis_showscale=False)
        st.plotly_chart(latency_fig, use_container_width=True)
else:
    st.info("No hosts have reported data yet.")

st.divider()

# --------------------------------------------------
# Fleet-wide Error Breakdown
# --------------------------------------------------

if report["error_breakdown"]:
    st.subheader("Fleet Error Breakdown")
    err_df = pd.DataFrame(
        list(report["error_breakdown"].items()),
        columns=["Error Type", "Count"],
    ).sort_values("Count", ascending=False)

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        err_fig = px.pie(
            err_df,
            names="Error Type",
            values="Count",
            hole=0.45,
            title="Fleet-wide Error Distribution",
        )
        err_fig.update_traces(textinfo="percent+label")
        st.plotly_chart(err_fig, use_container_width=True)
    with col_table:
        st.dataframe(err_df, hide_index=True, use_container_width=True)

    st.divider()

# --------------------------------------------------
# Per-Host Detail
# --------------------------------------------------

st.subheader("Host Detail")

if not hosts:
    st.info("No hosts have reported data yet.")
else:
    host_name = st.selectbox("Select a host", sorted(hosts.keys()))
    h = hosts[host_name]
    prev_h = prev_hosts.get(host_name) if prev_hosts else None

    badge = GRADE_BADGE.get(h["reliability_grade"], "⚪")
    status_line = f"### {badge} {host_name} — {h['reliability_grade']}"
    if h["currently_down"]:
        status_line += "  🔴 currently down"
    st.markdown(status_line)

    tab_overview, tab_latency, tab_loss_errors, tab_outages = st.tabs(
        ["📊 Overview", "📈 Latency", "📉 Loss & Errors", "🕳️ Outages"]
    )

    # ==================================================
    # Overview tab — headline numbers + how this host
    # compares to the rest of the fleet
    # ==================================================
    with tab_overview:
        st.caption(
            "Availability and latency for the selected monitoring period, "
            "compared against the previous poll and the fleet average."
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Uptime",
            f"{h['uptime_pct']}%",
            delta=_delta(h["uptime_pct"], prev_h["uptime_pct"] if prev_h else None, "{:+.2f} pp"),
            help="Percentage of pings that succeeded over the full monitoring period.",
        )
        c2.metric(
            "Avg Latency",
            f"{h['avg_latency_ms']} ms" if h["avg_latency_ms"] is not None else "N/A",
            delta=_delta(
                h["avg_latency_ms"],
                prev_h["avg_latency_ms"] if prev_h else None,
                "{:+.1f} ms",
            ),
            delta_color="inverse",
            help="Mean round-trip time across all successful pings. Lower is better.",
        )
        c3.metric(
            "P95 Latency",
            f"{h['p95_latency_ms']} ms" if h["p95_latency_ms"] is not None else "N/A",
            help="95% of pings responded faster than this. A good indicator of worst-case "
            "experience without being skewed by rare extreme spikes.",
        )
        c4.metric(
            "Outages",
            h["outage_count"],
            delta=_delta(h["outage_count"], prev_h["outage_count"] if prev_h else None, "{:+d}"),
            delta_color="inverse",
            help=f"Number of times this host had {analytics.outage_threshold}+ consecutive failed pings.",
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Pings", h["total_pings"], help="All pings recorded for this host, success or fail.")
        c2.metric("Failed Pings", h["failed_pings"])
        c3.metric(
            "Total Downtime",
            _human_duration(h.get("total_downtime_seconds")),
            help="Combined duration of all outages, including any still ongoing.",
        )
        c4.metric(
            "Longest Outage",
            f"{h['longest_outage_seconds']:.0f}s" if h["longest_outage_seconds"] else "None",
        )

        st.divider()
        st.markdown("**How this host compares to the fleet**")

        fleet_avg_latency = summary.get("fleet_avg_latency_ms")
        fleet_avg_uptime = summary.get("fleet_uptime_pct")

        cc1, cc2 = st.columns(2)
        with cc1:
            if h["avg_latency_ms"] is not None and fleet_avg_latency is not None:
                diff = h["avg_latency_ms"] - fleet_avg_latency
                direction = "slower than" if diff > 0 else "faster than" if diff < 0 else "the same as"
                st.metric(
                    "Latency vs. Fleet Average",
                    f"{h['avg_latency_ms']} ms",
                    delta=f"{diff:+.1f} ms vs {fleet_avg_latency} ms fleet avg",
                    delta_color="inverse",
                    help=f"This host is {abs(diff):.1f} ms {direction} the fleet average.",
                )
            else:
                st.metric("Latency vs. Fleet Average", "N/A")
        with cc2:
            if fleet_avg_uptime is not None:
                diff = h["uptime_pct"] - fleet_avg_uptime
                direction = "above" if diff > 0 else "below" if diff < 0 else "at"
                st.metric(
                    "Uptime vs. Fleet Average",
                    f"{h['uptime_pct']}%",
                    delta=f"{diff:+.2f} pp vs {fleet_avg_uptime}% fleet avg",
                    help=f"This host is {abs(diff):.2f} points {direction} the fleet average.",
                )
            else:
                st.metric("Uptime vs. Fleet Average", "N/A")

    # ==================================================
    # Latency tab — the time-series chart with reference
    # lines and shaded outage windows
    # ==================================================
    with tab_latency:
        if h["latency_series"]:
            st.caption(
                "Dotted line = this host's average latency. Dashed orange line = P95. "
                "Red shading marks recorded outage windows."
            )
            lat_df = pd.DataFrame(h["latency_series"])
            lat_df["t"] = pd.to_datetime(lat_df["t"])

            lat_fig = go.Figure()
            lat_fig.add_trace(
                go.Scatter(
                    x=lat_df["t"],
                    y=lat_df["avg_ms"],
                    mode="lines+markers",
                    name="Avg Latency",
                    line=dict(color="#2980b9", width=2),
                    marker=dict(size=4),
                    hovertemplate="%{x}<br>%{y:.1f} ms<extra></extra>",
                )
            )

            if h["avg_latency_ms"] is not None:
                lat_fig.add_hline(
                    y=h["avg_latency_ms"],
                    line_dash="dot",
                    line_color="gray",
                    annotation_text=f"Avg: {h['avg_latency_ms']} ms",
                    annotation_position="top left",
                )
            if h["p95_latency_ms"] is not None:
                lat_fig.add_hline(
                    y=h["p95_latency_ms"],
                    line_dash="dash",
                    line_color="orange",
                    annotation_text=f"P95: {h['p95_latency_ms']} ms",
                    annotation_position="bottom left",
                )

            # Shade each outage window in red (ongoing outages shade to "now")
            for outage in h["outages"]:
                lat_fig.add_vrect(
                    x0=outage["start_time"],
                    x1=outage["end_time"] or pd.Timestamp.utcnow().isoformat(),
                    fillcolor="red",
                    opacity=0.15,
                    line_width=0,
                )

            lat_fig.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title=None,
                yaxis_title="ms",
                showlegend=False,
            )
            st.plotly_chart(lat_fig, use_container_width=True)

            with st.expander("What am I looking at?"):
                st.write(
                    "Each point is the average latency across all successful pings in a "
                    "one-minute bucket. Gaps in the line mean no successful pings landed "
                    "in that window (often because the host was down)."
                )
        else:
            st.info("No successful pings recorded for this host yet.")

    # ==================================================
    # Loss & Errors tab
    # ==================================================
    with tab_loss_errors:
        if h["loss_series"]:
            st.markdown("**Packet loss over time**")
            loss_df = pd.DataFrame(h["loss_series"])
            loss_df["t"] = pd.to_datetime(loss_df["t"])

            loss_fig = go.Figure()
            loss_fig.add_trace(
                go.Scatter(
                    x=loss_df["t"],
                    y=loss_df["loss_pct"],
                    mode="lines",
                    fill="tozeroy",
                    name="Packet Loss",
                    line=dict(color="#c0392b", width=1.5),
                    hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>",
                )
            )
            loss_fig.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title=None,
                yaxis_title="%",
                showlegend=False,
            )
            st.plotly_chart(loss_fig, use_container_width=True)
        else:
            st.info("No packet loss data available for this host.")

        st.divider()

        if h["error_breakdown"]:
            st.markdown("**Error breakdown**")
            host_err_df = pd.DataFrame(list(h["error_breakdown"].items()), columns=["Error Type", "Count"])
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                host_err_fig = px.bar(
                    host_err_df.sort_values("Count"),
                    x="Count",
                    y="Error Type",
                    orientation="h",
                    title=None,
                )
                host_err_fig.update_layout(
                    height=max(200, 40 * len(host_err_df)), margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(host_err_fig, use_container_width=True)
            with col_table:
                st.dataframe(host_err_df, hide_index=True, use_container_width=True)
        else:
            st.success("No failed pings recorded for this host — no errors to show.")

    # ==================================================
    # Outages tab
    # ==================================================
    with tab_outages:
        if h["outages"]:
            st.caption(
                "'Ongoing' means the host is still down as of the last refresh — "
                "duration keeps growing until it recovers."
            )
            outage_df = pd.DataFrame(h["outages"])[["start_time", "end_time", "duration_seconds"]]
            outage_df["end_time"] = outage_df["end_time"].fillna("Ongoing")
            outage_df = outage_df.rename(
                columns={
                    "start_time": "Start",
                    "end_time": "End",
                    "duration_seconds": "Duration (s)",
                }
            )
            st.dataframe(outage_df, hide_index=True, use_container_width=True)
        else:
            st.success("No outages recorded for this host.")

st.divider()

# --------------------------------------------------
# Fleet-wide Outage Log
# --------------------------------------------------

st.subheader("Fleet Outage Log")

if report["outage_log"]:
    outage_log_df = pd.DataFrame(report["outage_log"])[
        ["host", "start_time", "end_time", "duration_seconds"]
    ]
    outage_log_df["end_time"] = outage_log_df["end_time"].fillna("Ongoing")
    st.dataframe(outage_log_df, hide_index=True, use_container_width=True)
else:
    st.info("No outages recorded across the fleet.")

st.divider()

# --------------------------------------------------
# Exports
# --------------------------------------------------

st.subheader("Exports")

report_gen = ReportGenerator(analytics)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Export Latency CSV"):
        path = report_gen.export_latency_csv()
        st.success(f"Saved to {path}")
        with open(path, "rb") as f:
            st.download_button("Download latency_logs.csv", f, file_name=path.name)

with col2:
    if st.button("Export Outage CSV"):
        path = report_gen.export_outage_csv()
        st.success(f"Saved to {path}")
        with open(path, "rb") as f:
            st.download_button("Download outage_logs.csv", f, file_name=path.name)

with col3:
    if st.button("Export Summary CSV"):
        path = report_gen.export_summary_csv()
        st.success(f"Saved to {path}")
        with open(path, "rb") as f:
            st.download_button("Download summary.csv", f, file_name=path.name)

with col4:
    if st.button("Export PDF Report"):
        try:
            path = report_gen.export_pdf_report()
            st.success(f"Saved to {path}")
            with open(path, "rb") as f:
                st.download_button("Download network_report.pdf", f, file_name=path.name)
        except Exception as e:
            st.error(f"PDF export failed: {e}")