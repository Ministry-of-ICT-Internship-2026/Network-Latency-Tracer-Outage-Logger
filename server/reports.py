import csv
import sqlite3
from pathlib import Path
from typing import Dict, List
from analytics import Analytics
from datetime import datetime

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
        analytics,
        export_folder: str = "exports",
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

        rows = self.database.get_all_pings()

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

        rows = self.database.get_all_outages()

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

        summary = self.analytics.overall_summary()

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
    Generates a professional PDF report containing
    summary statistics, outage information and graphs
    if available.
    """

    summary = self.analytics.overall_summary()

    output_file = self.export_folder / filename

    document = SimpleDocTemplate(
        str(output_file),
        pagesize=None,
    )

    from reportlab.lib.pagesizes import A4

    document.pagesize = A4

    styles = getSampleStyleSheet()

    story = []

 # --------------------------------------------------
 # Title
 # --------------------------------------------------

    story.append(
        Paragraph(
            "<b><font size=20>"
            "Network Latency Monitoring Report"
            "</font></b>",
            styles["Title"],
        )
    )
    story.append(
         Paragraph(
           f"Generated on: {datetime.now().strftime('%d %B %Y %H:%M')}",
        styles["Normal"],
    )
)

    story.append(Spacer(1, 0.3 * inch))

    story.append(
        Paragraph(
            "Automatically generated from the "
            "Network Latency Tracer & Outage Logger.",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 0.4 * inch))

# --------------------------------------------------
# Summary Table
 # --------------------------------------------------

    table_data = [

        ["Metric", "Value"],

        ["Total Checks", summary["total_checks"]],

        ["Successful Checks", summary["successful_checks"]],

        ["Failed Checks", summary["failed_checks"]],

        ["Average Latency (ms)", summary["average_latency"]],

        ["Minimum Latency (ms)", summary["minimum_latency"]],

        ["Maximum Latency (ms)", summary["maximum_latency"]],

        ["Uptime (%)", summary["uptime_percent"]],

        ["Total Outages", summary["total_outages"]],

        ["Total Downtime (seconds)", summary["total_downtime"]],

        ["Longest Outage (seconds)", summary["longest_outage"]],
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
                    f"<b>{graph.replace('.png','').replace('_',' ').title()}</b>",
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

    outages = self.database.get_all_outages()

    if outages:

        story.append(
            Paragraph(
                "<b>Recorded Outages</b>",
                styles["Heading1"],
            )
        )

        outage_table = [

            [
                "Host",
                "Start",
                "End",
                "Duration (s)",
            ]
        ]

        for outage in outages:

            outage_table.append(

                [

                    outage["host"],

                    outage["start_time"],

                    outage["end_time"],

                    round(outage["duration_seconds"], 2),

                ]

            )

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

    document.build(story)

    return output_file
    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    def close(self) -> None:
        """
        Close database connection.
        """
        self.connection.close()
