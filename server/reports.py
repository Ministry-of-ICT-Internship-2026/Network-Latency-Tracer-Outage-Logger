import csv
from pathlib import Path
from datetime import datetime

from server.analytics import MonitoringAnalytics

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

class ReportGenerator:

    def __init__(
       self,
       analytics: MonitoringAnalytics,
       export_folder="exports",
    ):
        self.analytics = analytics
        self.export_folder = Path(export_folder)

        # Create exports folder automatically
        self.export_folder.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # CSV Export Functions
    # --------------------------------------------------

    def export_latency_csv(
        self,
        filename: str = "latency_logs.csv",
    ) -> Path:
        """
        Export all latency logs to a CSV file.
        """

        rows = self.analytics.get_latency_logs()

        output_file = self.export_folder / filename

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow([
                "ID",
                "Host",
                "Sequence",
                "Timestamp",
                "Success",
                "Latency (ms)",
                "Error Type",
            ])

            for row in rows:
                writer.writerow([
                    row["id"],
                    row["host"],
                    row["sequence"],
                    row["timestamp"],
                    "Yes" if row["success"] else "No",
                    row["latency_ms"],
                    row["error_type"],
                ])

        return output_file

    def export_outage_csv(
        self,
        filename: str = "outage_logs.csv",
    ) -> Path:
        """
        Export all outage events to CSV.
        """

        rows = self.analytics.get_outage_logs()

        output_file = self.export_folder / filename

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow([
                "ID",
                "Host",
                "Start Time",
                "End Time",
                "Duration (Seconds)",
            ])

            for row in rows:
                writer.writerow([
                    row["id"],
                    row["host"],
                    row["start_time"],
                    row["end_time"],
                    row["duration_seconds"],
                ])

        return output_file

    def export_summary_csv(
        self,
        filename: str = "summary.csv",
    ) -> Path:
        """
        Export calculated statistics to CSV.
        """

        report = self.analytics.build_full_report()
        summary = report["summary"]
        

        output_file = self.export_folder / filename

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

            writer = csv.writer(csvfile)

            writer.writerow([
                "Metric",
                "Value",
            ])

            for key, value in summary.items():
                writer.writerow([
                    key.replace("_", " ").title(),
                    value,
                ])

        return output_file

    # --------------------------------------------------
    # PDF Report
    # --------------------------------------------------

    def export_pdf_report(
        self,
        filename: str = "network_report.pdf",
        graph_folder: str = "graphs",
    ) -> Path:
        """
        Generates a professional PDF report.
        """

        report = self.analytics.build_full_report()

        summary = report["summary"]
        hosts = report["hosts"]
        period = report["period"]

        output_file = self.export_folder / filename

        from reportlab.lib.pagesizes import A4

        document = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
        )

        styles = getSampleStyleSheet()
        story = []

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        story.append(
            Paragraph(
                "<b><font size=20>Network Latency Monitoring Report</font></b>",
                styles["Title"],
            )
        )

        story.append(
            Paragraph(
                f"Generated on: {datetime.now():%d %B %Y %H:%M}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        story.append(
            Paragraph(
                "Automatically generated from the Network Latency Tracer & Outage Logger.",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.4 * inch))

        # --------------------------------------------------
        # Executive Summary
        # --------------------------------------------------

        story.append(
            Paragraph(
                "Executive Summary",
                styles["Heading1"],
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        story.append(
           Paragraph(
                f"<b>Monitoring Period:</b> {period['start']} to {period['end']}",
                styles["Normal"],
             )
        )

        story.append(
            Paragraph(
                 f"<b>Hosts Monitored:</b> {summary.get('hosts_monitored', 'N/A')}",
                 styles["Normal"],
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        table_data = [
             ["Metric", "Value"],
             ["Hosts Monitored", summary["hosts_monitored"]],
             ["Total Ping Checks", summary["total_pings"]],
             ["Failed Pings", summary["total_failed_pings"]],
             ["Fleet Average Latency (ms)", summary["fleet_avg_latency_ms"]],
             ["Fleet Uptime (%)", summary["fleet_uptime_pct"]],
             ["Total Outages", summary["total_outages"]],
             ["Total Downtime", summary["total_downtime_human"]],
             ["Worst Host", summary["worst_host"]],
             ["Best Host", summary["best_host"]],
        ]

        table = Table(table_data)

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 0.4 * inch))

        story.append(
             Paragraph(
                 "Performance Graphs",
                 styles["Heading1"],
             )
        )

        story.append(Spacer(1, 0.2 * inch))

        # --------------------------------------------------
        # Graphs
        # --------------------------------------------------

        graph_folder = Path(graph_folder)

        graph_files = [
            "latency.png",
            "packet_loss.png",
            "uptime.png",
            "outages.png",
        ]

        for graph in graph_files:

            graph_path = graph_folder / graph

            if graph_path.exists():

                story.append(
                    Paragraph(
                        graph.replace(".png", "").replace("_", " ").title(),
                        styles["Heading2"],
                    )
                )

                story.append(
                    Image(
                        str(graph_path),
                        width=6.5 * inch,
                        height=3.5 * inch,
                    )
                )

                story.append(Spacer(1, 0.25 * inch))

        # --------------------------------------------------
        # Outage Details
        # --------------------------------------------------
        story.append(
            Paragraph(
                "Outage History",
                styles["Heading1"],
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        outages = []

        for host in hosts.values():
            outages.extend(host["outages"])

        if outages:

            story.append(
                Paragraph(
                    "Recorded Outages",
                    styles["Heading1"],
                )
            )

            outage_table = [
                ["Host", "Start Time", "End Time", "Duration (Seconds)"]
            ]

            for outage in outages:
                outage_table.append([
                    outage["host"],
                    outage["start_time"],
                    outage["end_time"] or "Ongoing",
                    round(outage["duration_seconds"], 2),
                ])

            t = Table(outage_table)

            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ]
                )
            )

            story.append(t)

            story.append(Spacer(1, 0.4 * inch))

        story.append(
             Paragraph(
                "<i>End of Report</i>",
                styles["Normal"],
             )
         )

        document.build(story)

        return output_file