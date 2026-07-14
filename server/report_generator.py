"""
report_generator.py — Renders MonitoringAnalytics output into a single,
self-contained HTML file: a reliability report with interactive charts
(Chart.js, bundled inline so it works with no internet connection).

Usage:
    python report_generator.py [--db PATH] [--output PATH] [--threshold N]

Designed to be run:
  - on demand, for accountability / handover reports
  - on a schedule (cron / Task Scheduler), for weekly planning packets
  - straight from a terminal on the Ministry network, offline

The output is one .html file. Open it in any browser; use the browser's
Print -> Save as PDF for a document to attach to a weekly report.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from analytics import MonitoringAnalytics
from config import MonitorConfig

ASSETS_DIR = Path(__file__).parent / "assets"
CHARTJS_PATH = ASSETS_DIR / "chartjs.min.js"


def _fmt_dt(iso_str: str | None) -> str:
    if not iso_str:
        return "—"
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%d %b %Y, %H:%M:%S UTC")


def _fmt_num(value, suffix: str = "", dash: str = "—") -> str:
    if value is None:
        return dash
    return f"{value}{suffix}"


def build_html(report: dict) -> str:
    chartjs_src = CHARTJS_PATH.read_text(encoding="utf-8")
    data_json = json.dumps(report, default=str)

    summary = report["summary"]
    period = report["period"]
    hosts = report["hosts"]
    host_names = list(hosts.keys())

    # ---- KPI cards ----
    kpi_cards = f"""
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-label">Fleet availability</span>
          <span class="kpi-value">{_fmt_num(summary['fleet_uptime_pct'], '%')}</span>
          <span class="kpi-sub">{summary['hosts_monitored']} host(s) monitored</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Avg latency</span>
          <span class="kpi-value">{_fmt_num(summary['fleet_avg_latency_ms'], ' ms')}</span>
          <span class="kpi-sub">fleet-wide mean</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Outages logged</span>
          <span class="kpi-value">{summary['total_outages']}</span>
          <span class="kpi-sub">{summary['total_downtime_human']} total downtime</span>
        </div>
        <div class="kpi-card {'kpi-alert' if summary['currently_down_hosts'] else ''}">
          <span class="kpi-label">Currently down</span>
          <span class="kpi-value">{len(summary['currently_down_hosts'])}</span>
          <span class="kpi-sub">{', '.join(summary['currently_down_hosts']) or 'all hosts responding'}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Best performer</span>
          <span class="kpi-value kpi-value-sm">{summary['best_host'] or '—'}</span>
          <span class="kpi-sub">{_fmt_num(summary['best_host_uptime_pct'], '%')} uptime</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Needs attention</span>
          <span class="kpi-value kpi-value-sm">{summary['worst_host'] or '—'}</span>
          <span class="kpi-sub">{_fmt_num(summary['worst_host_uptime_pct'], '%')} uptime</span>
        </div>
      </div>
    """

    # ---- Per-host panels ----
    grade_class = {
        "Excellent": "grade-excellent",
        "Good": "grade-good",
        "Fair": "grade-fair",
        "Poor": "grade-poor",
        "Critical": "grade-critical",
        "N/A": "grade-na",
    }

    host_panels = []
    for host in host_names:
        h = hosts[host]
        status_class = "status-down" if h["currently_down"] else "status-up"
        status_text = "DOWN" if h["currently_down"] else "UP"
        outages_rows = "".join(
            f"""<tr>
                  <td>{_fmt_dt(o['start_time'])}</td>
                  <td>{_fmt_dt(o['end_time'])}</td>
                  <td>{o['duration_seconds']:.1f}s</td>
                </tr>"""
            for o in h["outages"]
        ) or '<tr><td colspan="3" class="empty-row">No completed outages in this window</td></tr>'

        errors_line = (
            ", ".join(f"{k}: {v}" for k, v in h["error_breakdown"].items())
            if h["error_breakdown"] else "none"
        )

        host_panels.append(f"""
        <section class="host-panel">
          <header class="host-panel__header">
            <div class="host-panel__id">
              <span class="status-dot {status_class}"></span>
              <h3>{host}</h3>
              <span class="badge {grade_class.get(h['reliability_grade'], '')}">{h['reliability_grade']}</span>
            </div>
            <div class="host-panel__live">{status_text}{' · ' + str(h['current_consecutive_failures']) + ' consecutive failures' if h['currently_down'] else ''}</div>
          </header>

          <div class="host-panel__stats">
            <div class="stat"><span class="stat-label">Uptime</span><span class="stat-value">{_fmt_num(h['uptime_pct'], '%')}</span></div>
            <div class="stat"><span class="stat-label">Avg latency</span><span class="stat-value">{_fmt_num(h['avg_latency_ms'], ' ms')}</span></div>
            <div class="stat"><span class="stat-label">P95 latency</span><span class="stat-value">{_fmt_num(h['p95_latency_ms'], ' ms')}</span></div>
            <div class="stat"><span class="stat-label">Jitter</span><span class="stat-value">{_fmt_num(h['avg_jitter_ms'], ' ms')}</span></div>
            <div class="stat"><span class="stat-label">Min / Max</span><span class="stat-value">{_fmt_num(h['min_latency_ms'])} / {_fmt_num(h['max_latency_ms'])}</span></div>
            <div class="stat"><span class="stat-label">Outages</span><span class="stat-value">{h['outage_count']}</span></div>
            <div class="stat"><span class="stat-label">MTTR</span><span class="stat-value">{_fmt_num(h['mttr_seconds'], 's')}</span></div>
            <div class="stat"><span class="stat-label">Longest outage</span><span class="stat-value">{_fmt_num(h['longest_outage_seconds'], 's')}</span></div>
          </div>

          <div class="host-panel__charts">
            <div class="chart-box">
              <span class="chart-title">Latency over time</span>
              <canvas id="latency-{host.replace('.', '-')}"></canvas>
            </div>
            <div class="chart-box">
              <span class="chart-title">Packet loss over time</span>
              <canvas id="loss-{host.replace('.', '-')}"></canvas>
            </div>
          </div>

          <div class="host-panel__footer">
            <div class="outage-table-wrap">
              <span class="chart-title">Outage log</span>
              <table class="data-table">
                <thead><tr><th>Start</th><th>End</th><th>Duration</th></tr></thead>
                <tbody>{outages_rows}</tbody>
              </table>
            </div>
            <div class="error-note"><span class="chart-title">Failure causes</span><p>{errors_line}</p></div>
          </div>
        </section>
        """)

    host_panels_html = "\n".join(host_panels)

    error_breakdown = report["error_breakdown"]
    has_errors = bool(error_breakdown)

    generated_at_fmt = _fmt_dt(report["generated_at"])
    period_fmt = f"{_fmt_dt(period['start'])} → {_fmt_dt(period['end'])} ({period['duration_hours']} h)" if period["start"] else "No data"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Network Reliability Report — {generated_at_fmt}</title>
<style>
{CSS}
</style>
</head>
<body>
  <div class="pulse-strip" aria-hidden="true">
    <svg viewBox="0 0 1200 40" preserveAspectRatio="none">
      <polyline points="0,20 100,20 120,20 135,4 150,36 165,20 900,20 920,20 935,4 950,36 965,20 1200,20"
        fill="none" stroke="var(--accent-cyan)" stroke-width="2"/>
    </svg>
  </div>

  <header class="masthead">
    <div class="masthead__eyebrow">Network Latency Tracer &amp; Outage Logger</div>
    <h1>Network Reliability Report</h1>
    <div class="masthead__meta">
      <div><span class="meta-label">Generated</span>{generated_at_fmt}</div>
      <div><span class="meta-label">Monitoring window</span>{period_fmt}</div>
      <div><span class="meta-label">Outage threshold</span>{report.get('outage_threshold', '—')} consecutive failed probes</div>
    </div>
    <button class="print-btn no-print" onclick="window.print()">Export / Print report</button>
  </header>

  <main>
    <section class="section">
      <h2 class="section-title"><span class="section-num">01</span> Executive summary</h2>
      {kpi_cards}
    </section>

    <section class="section">
      <h2 class="section-title"><span class="section-num">02</span> Fleet comparison</h2>
      <div class="fleet-charts">
        <div class="chart-box chart-box--lg">
          <span class="chart-title">Availability by host</span>
          <canvas id="fleet-uptime"></canvas>
        </div>
        <div class="chart-box chart-box--lg">
          <span class="chart-title">Average latency by host (ms)</span>
          <canvas id="fleet-latency"></canvas>
        </div>
        <div class="chart-box chart-box--lg">
          <span class="chart-title">Failure cause breakdown</span>
          {'<canvas id="fleet-errors"></canvas>' if has_errors else '<p class="empty-row">No failed probes recorded</p>'}
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title"><span class="section-num">03</span> Per-host detail</h2>
      {host_panels_html}
    </section>

    <section class="section">
      <h2 class="section-title"><span class="section-num">04</span> Notes for planning</h2>
      <div class="notes-panel">
        <ul>
          <li>MTTR (mean time to recovery) and MTBF (mean time between failures) are computed only from outages that both started and ended inside this monitoring window — use longer collection periods for statistically stronger figures.</li>
          <li>A host is counted as an outage once probe failures reach the configured consecutive-failure threshold; brief single-probe timeouts are normal network jitter and are not counted as outages.</li>
          <li>"Currently down" hosts were still inside an active failure streak at report generation time and have not yet produced a completed outage record — follow up before closing this reporting period.</li>
        </ul>
      </div>
    </section>
  </main>

  <footer class="report-footer no-print">
    Generated automatically from <code>latency.db</code> — Network Latency Tracer &amp; Outage Logger.
  </footer>

<script>
{chartjs_src}
</script>
<script>
const REPORT = {data_json};

Chart.defaults.color = '#8A97A8';
Chart.defaults.font.family = "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace";
Chart.defaults.font.size = 11;
Chart.defaults.borderColor = 'rgba(138,151,168,0.12)';

function tsLabel(iso) {{
  const d = new Date(iso);
  return d.toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
}}

// Fleet uptime bar
(() => {{
  const hosts = Object.keys(REPORT.hosts);
  const uptimes = hosts.map(h => REPORT.hosts[h].uptime_pct);
  new Chart(document.getElementById('fleet-uptime'), {{
    type: 'bar',
    data: {{
      labels: hosts,
      datasets: [{{
        data: uptimes,
        backgroundColor: uptimes.map(u => u >= 99 ? '#4FD1AE' : u >= 90 ? '#E8A33D' : '#E85D5D'),
        borderRadius: 4,
        maxBarThickness: 36,
      }}]
    }},
    options: {{
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ y: {{ min: 0, max: 100, ticks: {{ callback: v => v + '%' }} }} }},
      responsive: true,
      maintainAspectRatio: false,
    }}
  }});
}})();

// Fleet latency bar
(() => {{
  const hosts = Object.keys(REPORT.hosts);
  const lat = hosts.map(h => REPORT.hosts[h].avg_latency_ms);
  new Chart(document.getElementById('fleet-latency'), {{
    type: 'bar',
    data: {{
      labels: hosts,
      datasets: [{{
        data: lat,
        backgroundColor: '#4FB3E8',
        borderRadius: 4,
        maxBarThickness: 36,
      }}]
    }},
    options: {{
      plugins: {{ legend: {{ display: false }} }},
      responsive: true,
      maintainAspectRatio: false,
    }}
  }});
}})();

// Fleet error breakdown donut
(() => {{
  const el = document.getElementById('fleet-errors');
  if (!el) return;
  const errs = REPORT.error_breakdown;
  new Chart(el, {{
    type: 'doughnut',
    data: {{
      labels: Object.keys(errs),
      datasets: [{{
        data: Object.values(errs),
        backgroundColor: ['#E85D5D', '#E8A33D', '#8A97A8', '#4FB3E8'],
        borderColor: '#171f29',
        borderWidth: 2,
      }}]
    }},
    options: {{
      plugins: {{ legend: {{ position: 'bottom' }} }},
      responsive: true,
      maintainAspectRatio: false,
    }}
  }});
}})();

// Per-host latency + loss series
Object.keys(REPORT.hosts).forEach(host => {{
  const h = REPORT.hosts[host];
  const id = host.replace(/\\./g, '-');

  const latEl = document.getElementById('latency-' + id);
  if (latEl) {{
    new Chart(latEl, {{
      type: 'line',
      data: {{
        labels: h.latency_series.map(p => tsLabel(p.t)),
        datasets: [{{
          data: h.latency_series.map(p => p.avg_ms),
          borderColor: '#4FB3E8',
          backgroundColor: 'rgba(79,179,232,0.12)',
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          borderWidth: 2,
        }}]
      }},
      options: {{
        plugins: {{ legend: {{ display: false }} }},
        scales: {{ x: {{ ticks: {{ maxTicksLimit: 6 }} }}, y: {{ title: {{ display: true, text: 'ms' }} }} }},
        responsive: true,
        maintainAspectRatio: false,
      }}
    }});
  }}

  const lossEl = document.getElementById('loss-' + id);
  if (lossEl) {{
    new Chart(lossEl, {{
      type: 'bar',
      data: {{
        labels: h.loss_series.map(p => tsLabel(p.t)),
        datasets: [{{
          data: h.loss_series.map(p => p.loss_pct),
          backgroundColor: h.loss_series.map(p => p.loss_pct > 0 ? '#E85D5D' : 'rgba(79,209,174,0.5)'),
          maxBarThickness: 18,
        }}]
      }},
      options: {{
        plugins: {{ legend: {{ display: false }} }},
        scales: {{ x: {{ ticks: {{ maxTicksLimit: 6 }} }}, y: {{ min: 0, max: 100, ticks: {{ callback: v => v + '%' }} }} }},
        responsive: true,
        maintainAspectRatio: false,
      }}
    }});
  }}
}});
</script>
</body>
</html>
"""
    return html


CSS = """
:root {
  --bg: #10151c;
  --surface: #171f29;
  --surface-2: #1d2733;
  --border: rgba(138,151,168,0.14);
  --text: #EDF1F5;
  --text-muted: #8A97A8;
  --accent-cyan: #4FB3E8;
  --accent-green: #4FD1AE;
  --accent-amber: #E8A33D;
  --accent-red: #E85D5D;
  --radius: 10px;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --font-sans: 'IBM Plex Sans', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  line-height: 1.5;
}

.pulse-strip {
  width: 100%;
  height: 32px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  overflow: hidden;
}
.pulse-strip svg { width: 100%; height: 100%; opacity: 0.55; }

.masthead {
  padding: 40px 48px 28px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.masthead__eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent-cyan);
  margin-bottom: 10px;
}
.masthead h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 18px;
  letter-spacing: -0.01em;
}
.masthead__meta {
  display: flex;
  gap: 36px;
  flex-wrap: wrap;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text);
}
.meta-label {
  display: block;
  color: var(--text-muted);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 4px;
}
.print-btn {
  position: absolute;
  top: 40px;
  right: 48px;
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 10px 18px;
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: 12px;
  cursor: pointer;
}
.print-btn:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }

main { padding: 8px 48px 60px; max-width: 1320px; margin: 0 auto; }

.section { margin-top: 44px; }
.section-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  font-size: 15px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  padding-bottom: 12px;
  margin-bottom: 22px;
}
.section-num {
  font-family: var(--font-mono);
  color: var(--accent-cyan);
  font-size: 13px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 14px;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi-card.kpi-alert { border-color: rgba(232,93,93,0.5); background: rgba(232,93,93,0.06); }
.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); }
.kpi-value { font-family: var(--font-mono); font-size: 28px; font-weight: 600; }
.kpi-value-sm { font-size: 18px; }
.kpi-sub { font-size: 12px; color: var(--text-muted); }

.fleet-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.chart-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
  height: 220px;
  display: flex;
  flex-direction: column;
}
.chart-box--lg { height: 260px; }
.chart-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 10px;
}
.chart-box canvas { flex: 1; min-height: 0; }

.host-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px 26px;
  margin-bottom: 20px;
}
.host-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}
.host-panel__id { display: flex; align-items: center; gap: 10px; }
.host-panel__id h3 { margin: 0; font-family: var(--font-mono); font-size: 18px; font-weight: 600; }
.host-panel__live { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }

.status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.status-up { background: var(--accent-green); box-shadow: 0 0 0 3px rgba(79,209,174,0.18); }
.status-down { background: var(--accent-red); box-shadow: 0 0 0 3px rgba(232,93,93,0.22); animation: pulse-dot 1.4s ease-in-out infinite; }
@keyframes pulse-dot { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

.badge {
  font-family: var(--font-mono);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 3px 9px;
  border-radius: 100px;
  border: 1px solid var(--border);
}
.grade-excellent { color: var(--accent-green); border-color: rgba(79,209,174,0.4); }
.grade-good { color: var(--accent-cyan); border-color: rgba(79,179,232,0.4); }
.grade-fair { color: var(--accent-amber); border-color: rgba(232,163,61,0.4); }
.grade-poor, .grade-critical { color: var(--accent-red); border-color: rgba(232,93,93,0.4); }

.host-panel__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--surface-2);
  border-radius: 8px;
}
.stat { display: flex; flex-direction: column; gap: 3px; }
.stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }
.stat-value { font-family: var(--font-mono); font-size: 15px; }

.host-panel__charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 18px;
}
.host-panel__charts .chart-box { height: 180px; }

.host-panel__footer {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}
.data-table { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; }
.data-table th {
  text-align: left;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border);
}
.data-table td { padding: 7px 8px; border-bottom: 1px solid var(--border); }
.empty-row { color: var(--text-muted); font-style: italic; }
.error-note p { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); margin: 0; }

.notes-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
}
.notes-panel ul { margin: 0; padding-left: 20px; color: var(--text-muted); font-size: 13px; }
.notes-panel li { margin-bottom: 10px; }

.report-footer {
  text-align: center;
  padding: 30px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
}

@media (max-width: 900px) {
  .masthead, main { padding-left: 20px; padding-right: 20px; }
  .print-btn { position: static; margin-top: 16px; }
  .host-panel__charts, .host-panel__footer { grid-template-columns: 1fr; }
}

@media print {
  .no-print { display: none !important; }
  body { background: white; color: #111; }
  .kpi-card, .chart-box, .host-panel, .notes-panel { break-inside: avoid; border-color: #ccc; background: #fafafa; }
  .pulse-strip { display: none; }
}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a network reliability HTML report.")
    parser.add_argument("--db", default="database/latency.db", help="Path to latency.db")
    parser.add_argument("--output", default="reports/network_reliability_report.html", help="Output HTML path")
    _default_config = MonitorConfig(hosts=[])
    parser.add_argument(
        "--threshold", type=int, default=_default_config.outage_threshold,
        help="Consecutive failures counted as an outage (defaults to config.py's MonitorConfig)",
    )
    parser.add_argument("--bucket-seconds", type=int, default=60, help="Time-series bucket width in seconds")
    args = parser.parse_args()

    with MonitoringAnalytics(args.db, outage_threshold=args.threshold) as analytics:
        report = analytics.build_full_report(bucket_seconds=args.bucket_seconds)
    report["outage_threshold"] = args.threshold

    html = build_html(report)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Report written to {out_path.resolve()}")


if __name__ == "__main__":
    main()
