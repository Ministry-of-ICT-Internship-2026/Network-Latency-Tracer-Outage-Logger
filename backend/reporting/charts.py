import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile
from datetime import datetime




# ==================================================
# HELPERS
# ==================================================

def _format_time_label(raw):
    """Turn an ISO timestamp into a short, readable label.
    Falls back to the raw string if it doesn't parse."""

    try:

        dt = datetime.fromisoformat(raw)

        return dt.strftime("%m-%d %H:%M")

    except (ValueError, TypeError):

        return raw



def _sparse_ticks(times, max_labels=8):
    """Return (positions, labels) for at most max_labels evenly spaced
    points, instead of labeling every single data point. This is what
    stops the x-axis from becoming an illegible wall of text."""

    n = len(times)


    if n == 0:

        return [], []


    step = max(
        1,
        n // max_labels
    )


    positions = list(
        range(0, n, step)
    )


    labels = [
        _format_time_label(times[i])
        for i in positions
    ]


    return positions, labels



def _style_axes(ax):

    ax.spines["top"].set_visible(False)

    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color("#cbd5e1")

    ax.spines["bottom"].set_color("#cbd5e1")

    ax.grid(
        True,
        color="#e2e8f0",
        linewidth=0.8
    )

    ax.set_axisbelow(True)

    ax.tick_params(
        axis="both",
        labelsize=9,
        colors="#475569"
    )




# ==================================================
# LATENCY CHART
# ==================================================

def create_latency_chart(host):

    series = host.get(
        "latency_series",
        []
    )[-100:]


    if not series:
        return None


    times = [
        item.get("t", "")
        for item in series
    ]


    values = [
        item.get("avg_ms", 0)
        for item in series
    ]


    fig, ax = plt.subplots(
        figsize=(8,3)
    )


    ax.plot(
        range(len(values)),
        values,
        color="#2563eb",
        linewidth=1.6,
        marker="o",
        markersize=3
    )


    ax.set_title(
        "Latency Trend",
        fontsize=11,
        color="#0f172a",
        fontweight="bold",
        loc="left"
    )


    ax.set_ylabel(
        "Milliseconds",
        fontsize=9,
        color="#475569"
    )


    positions, labels = _sparse_ticks(times)


    ax.set_xticks(positions)

    ax.set_xticklabels(
        labels,
        rotation=30,
        ha="right",
        fontsize=8
    )


    _style_axes(ax)


    fig.tight_layout()


    temp = NamedTemporaryFile(
        suffix=".png",
        delete=False
    )


    fig.savefig(
        temp.name,
        dpi=150,
        bbox_inches="tight"
    )


    plt.close(fig)


    return temp.name




# ==================================================
# PACKET LOSS CHART
# ==================================================

def create_loss_chart(host):

    series = host.get(
        "loss_series",
        []
    )[-100:]


    if not series:
        return None


    times = [
        item.get("t", "")
        for item in series
    ]


    values = [
        item.get("loss_pct", 0)
        for item in series
    ]


    fig, ax = plt.subplots(
        figsize=(8,3)
    )


    ax.plot(
        range(len(values)),
        values,
        color="#dc2626",
        linewidth=1.6,
        marker="o",
        markersize=3
    )


    ax.set_title(
        "Packet Loss",
        fontsize=11,
        color="#0f172a",
        fontweight="bold",
        loc="left"
    )


    ax.set_ylabel(
        "Loss (%)",
        fontsize=9,
        color="#475569"
    )


    positions, labels = _sparse_ticks(times)


    ax.set_xticks(positions)

    ax.set_xticklabels(
        labels,
        rotation=30,
        ha="right",
        fontsize=8
    )


    _style_axes(ax)


    fig.tight_layout()


    temp = NamedTemporaryFile(
        suffix=".png",
        delete=False
    )


    fig.savefig(
        temp.name,
        dpi=150,
        bbox_inches="tight"
    )


    plt.close(fig)


    return temp.name