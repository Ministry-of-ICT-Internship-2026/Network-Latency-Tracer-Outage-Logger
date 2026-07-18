import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



GRADE_COLORS = {
    "Excellent": "#2ecc71",
    "Good": "#27ae60",
    "Fair": "#f1c40f",
    "Poor": "#e67e22",
    "Critical": "#e74c3c",
    "N/A": "#95a5a6",
}



def _chart_height(count):
    """
    Dynamic chart height based on number of items.
    """

    return max(
        300,
        40 * count
    )



# ==================================================
# Fleet Comparison
# ==================================================

def render_fleet_comparison(hosts):
    """
    Creates fleet uptime and latency comparison charts.
    """


    if not hosts:
        return None, None



    rows = []


    for host in hosts.values():

        rows.append(
            {
                "Host": host.get(
                    "host",
                    "Unknown"
                ),

                "Uptime (%)": host.get(
                    "uptime_pct",
                    0
                ),

                "Latency (ms)": (
                    host.get(
                        "avg_latency_ms"
                    )
                    or 0
                ),

                "Grade": host.get(
                    "reliability_grade",
                    "N/A"
                ),
            }
        )


    df = pd.DataFrame(rows)



    uptime_fig = px.bar(
        df.sort_values(
            "Uptime (%)"
        ),
        x="Uptime (%)",
        y="Host",
        orientation="h",
        color="Grade",
        color_discrete_map=GRADE_COLORS,
        text="Uptime (%)",
        title="Uptime by Host",
    )


    uptime_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
    )


    uptime_fig.update_layout(
        height=_chart_height(
            len(df)
        ),
        xaxis_range=[
            max(
                0,
                df["Uptime (%)"].min() - 5
            ),
            100,
        ],
    )



    latency_fig = px.bar(
        df.sort_values(
            "Latency (ms)",
            ascending=False
        ),
        x="Latency (ms)",
        y="Host",
        orientation="h",
        text="Latency (ms)",
        title="Average Latency by Host",
    )


    latency_fig.update_traces(
        texttemplate="%{text:.1f} ms",
        textposition="outside",
    )


    latency_fig.update_layout(
        height=_chart_height(
            len(df)
        ),
    )


    return uptime_fig, latency_fig




# ==================================================
# Error Distribution
# ==================================================

def render_error_chart(error_breakdown):
    """
    Creates error distribution pie chart.
    """


    if not error_breakdown:
        return None



    df = pd.DataFrame(
        list(error_breakdown.items()),
        columns=[
            "Error",
            "Count"
        ],
    )



    fig = px.pie(
        df,
        names="Error",
        values="Count",
        hole=0.45,
        title="Network Error Distribution",
    )


    fig.update_traces(
        textinfo="percent+label"
    )


    return fig




# ==================================================
# Host Latency Trend
# ==================================================

def render_latency_chart(host):
    """
    Creates latency trend chart for a host.
    """


    series = host.get(
        "latency_series",
        []
    )


    if not series:
        return None



    df = pd.DataFrame(
        series
    )


    df["t"] = pd.to_datetime(
        df["t"]
    )



    fig = go.Figure()



    fig.add_trace(
        go.Scatter(
            x=df["t"],
            y=df["avg_ms"],
            mode="lines+markers",
            name="Latency",
            hovertemplate=
            "%{x}<br>%{y:.2f} ms"
            "<extra></extra>",
        )
    )



    avg = host.get(
        "avg_latency_ms"
    )


    if avg is not None:

        fig.add_hline(
            y=avg,
            line_dash="dot",
            annotation_text=f"Average {avg} ms",
        )



    p95 = host.get(
        "p95_latency_ms"
    )


    if p95 is not None:

        fig.add_hline(
            y=p95,
            line_dash="dash",
            annotation_text=f"P95 {p95} ms",
        )



    # Add outage shading
    for outage in host.get(
        "outages",
        []
    ):

        fig.add_vrect(
            x0=outage["start_time"],
            x1=(
                outage["end_time"]
                or pd.Timestamp.utcnow()
            ),
            opacity=0.15,
            line_width=0,
        )



    fig.update_layout(
        height=400,
        yaxis_title="Milliseconds",
        xaxis_title=None,
    )


    return fig




# ==================================================
# Packet Loss Trend
# ==================================================

def render_loss_chart(host):
    """
    Creates packet loss chart.
    """


    series = host.get(
        "loss_series",
        []
    )


    if not series:
        return None



    df = pd.DataFrame(
        series
    )


    df["t"] = pd.to_datetime(
        df["t"]
    )



    fig = go.Figure()



    fig.add_trace(
        go.Scatter(
            x=df["t"],
            y=df["loss_pct"],
            mode="lines",
            fill="tozeroy",
            name="Packet Loss",
            hovertemplate=
            "%{x}<br>%{y:.1f}%"
            "<extra></extra>",
        )
    )



    fig.update_layout(
        height=300,
        yaxis_title="Loss %",
        xaxis_title=None,
    )


    return fig