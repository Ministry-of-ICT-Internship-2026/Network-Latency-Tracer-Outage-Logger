import csv
from pathlib import Path
import sqlite3
from statistics import mean
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4  # CHANGED: moved this import to the top of the file
                                         # (previously imported mid-function inside export_pdf_report)
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
    """
    Generates reports from the monitoring database.
    """

    def __init__(
        self,
        database_path: str = "database/latency.db",
        export_folder: str = "exports",
    ):
        self.database_path = database_path
        self.export_folder = Path(export_folder)

        # Create exports folder automatically
        self.export_folder.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row

    # --------------------------------------------------
    # Database Queries
    # --------------------------------------------------

    def get_latency_logs(self) -> List[sqlite3.Row]:
        """
        Returns every latency record.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM latency_logs
            ORDER BY timestamp ASC
        """)

        return cursor.fetchall()

    def get_outage_logs(self) -> List[sqlite3.Row]:
        """
        Returns every outage record.
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM outage_logs
            ORDER BY start_time ASC
        """)

        return cursor.fetchall()

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def latency_statistics(self) -> Dict:
        """
        Calculates latency statistics.
        """

        rows = self.get_latency_logs()

        if not rows:
            return {
                "total_checks": 0,
                "successful_checks": 0,
                "failed_checks": 0,
                "average_latency": None,
                "minimum_latency": None,
                "maximum_latency": None,
                "uptime_percent": 0,
            }

        successful = [
            row["latency_ms"]
            for row in rows
            if row["success"] == 1 and row["latency_ms"] is not None
        ]

        total = len(rows)
        success = len(successful)
        failed = total - success

        return {
            "total_checks": total,

            "successful_checks": success,

            "failed_checks": failed,

            "average_latency":
                round(mean(successful), 2)
                if successful else None,

            "minimum_latency":
                round(min(successful), 2)
                if successful else None,

            "maximum_latency":
                round(max(successful), 2)
                if successful else None,

            "uptime_percent":
                round((success / total) * 100, 2)
                if total else 0,
        }

    def outage_statistics(self) -> Dict:
        """
        Calculates outage statistics.
        """

        rows = self.get_outage_logs()

        if not rows:
            return {
                "total_outages": 0,
                "total_downtime": 0,
                "longest_outage": 0,
            }

        durations = [
            row["duration_seconds"]
            for row in rows
        ]

        return {
            "total_outages": len(rows),

            "total_downtime":
                round(sum(durations), 2),

            "longest_outage":
                round(max(durations), 2),
        }

    def overall_summary(self) -> Dict:
        """
        Returns one dictionary containing all project statistics.
        """

        latency = self.latency_statistics()
        outages = self.outage_statistics()

        return {
            **latency,
            **outages
        }

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

        rows = self.get_latency_logs()

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

        rows = self.get_outage_logs()

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

        summary = self.overall_summary()

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

    # CHANGED: this whole method used to start at column 0 (outside the
    # class body), which made it a standalone module-level function
    # rather than a method of ReportGenerator. Calling
    # report.export_pdf_report() would have raised an AttributeError.
    # Re-indenting the "def" line to 4 spaces (and its entire body to
    # 8 spaces) puts it back inside the class.
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

        summary = self.overall_summary()

        output_file = self.export_folder / filename

        # CHANGED: previously created with pagesize=None, then the code
        # tried to patch it afterwards with `document.pagesize = A4`,
        # which doesn't reliably reconfigure a SimpleDocTemplate that's
        # already been constructed. Now A4 is passed directly here.
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
                "<b><font size=20>"
                "Network Latency Monitoring Report"
                "</font></b>",
                styles["Title"],
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

        outages = self.get_outage_logs()

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

        # NOTE: originally, a "close()" method was written directly after
        # this "return output_file" line, still indented at the same level
        # as this method's body. That made Python parse "close()" as a
        # function nested INSIDE export_pdf_report (and unreachable, since
        # it came after the return) rather than as a method of the class.
        # It has been moved out and properly re-indented below.

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    # CHANGED: re-indented to 4 spaces so it's a proper method of
    # ReportGenerator again (was accidentally nested inside
    # export_pdf_report — see note above).
    def close(self) -> None:
        """
        Close database connection.
        """
        self.connection.close()