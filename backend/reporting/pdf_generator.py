from io import BytesIO
from datetime import datetime, timezone
from tempfile import NamedTemporaryFile

import matplotlib.pyplot as plt


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER



# ==================================================
# CHART GENERATORS
# ==================================================

def create_latency_chart(host):

    series = host.get(
        "latency_series",
        []
    )


    if not series:
        return None



    times = [
        item.get(
            "timestamp",
            item.get("t", "")
        )
        for item in series
    ]


    values = [
        item.get(
            "latency_ms",
            item.get("avg_ms", 0)
        )
        for item in series
    ]



    plt.figure(
        figsize=(7,3)
    )


    plt.plot(
        times,
        values
    )


    plt.title(
        "Latency Trend"
    )


    plt.xlabel(
        "Time"
    )


    plt.ylabel(
        "Latency (ms)"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()



    temp = NamedTemporaryFile(
        suffix=".png",
        delete=False
    )


    plt.savefig(
        temp.name,
        dpi=300,
        bbox_inches="tight"
    )


    plt.close()


    return temp.name





def create_loss_chart(host):

    series = host.get(
        "loss_series",
        []
    )


    if not series:
        return None



    times = [
        item.get(
            "timestamp",
            item.get("t", "")
        )
        for item in series
    ]



    values = [
        item.get(
            "loss_pct",
            0
        )
        for item in series
    ]



    plt.figure(
        figsize=(7,3)
    )


    plt.plot(
        times,
        values
    )


    plt.title(
        "Packet Loss"
    )


    plt.xlabel(
        "Time"
    )


    plt.ylabel(
        "Loss (%)"
    )


    plt.xticks(
        rotation=45
    )


    plt.tight_layout()



    temp = NamedTemporaryFile(
        suffix=".png",
        delete=False
    )


    plt.savefig(
        temp.name,
        dpi=300,
        bbox_inches="tight"
    )


    plt.close()


    return temp.name





# ==================================================
# PAGE NUMBER
# ==================================================

def add_page_number(canvas, doc):

    canvas.saveState()


    canvas.setFont(
        "Helvetica",
        9
    )


    canvas.drawString(
        40,
        20,
        f"Network Monitor Report - Page {doc.page}"
    )


    canvas.restoreState()





# ==================================================
# PDF GENERATOR
# ==================================================

def generate_pdf(report):


    buffer = BytesIO()



    document = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=40,

        leftMargin=40,

        topMargin=50,

        bottomMargin=50

    )



    styles = getSampleStyleSheet()



    styles["Title"].alignment = TA_CENTER



    content = []



    # ------------------------------------------------
    # TITLE
    # ------------------------------------------------

    content.append(

        Paragraph(

            "Network Reliability Report",

            styles["Title"]

        )

    )



    content.append(

        Spacer(
            1,
            15
        )

    )



    generated = datetime.now(

        timezone.utc

    ).strftime(

        "%d %B %Y %H:%M UTC"

    )



    content.append(

        Paragraph(

            f"Generated: {generated}",

            styles["Normal"]

        )

    )



    content.append(

        Spacer(
            1,
            30
        )

    )





    summary = report["summary"]





    # ------------------------------------------------
    # SUMMARY
    # ------------------------------------------------

    content.append(

        Paragraph(

            "Executive Summary",

            styles["Heading2"]

        )

    )



    summary_table = Table(

        [

            ["Metric","Value"],


            [
                "Hosts monitored",
                summary["hosts_monitored"]
            ],


            [
                "Fleet uptime",
                f'{summary["fleet_uptime_pct"]}%'
            ],


            [
                "Average latency",
                f'{summary["fleet_avg_latency_ms"]} ms'
            ],


            [
                "Total outages",
                summary["total_outages"]
            ],


            [
                "Downtime",
                summary["total_downtime_human"]
            ]

        ],

        colWidths=[220,150]

    )



    summary_table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    None
                )

            ]

        )

    )



    content.append(

        summary_table

    )




    # ------------------------------------------------
    # HEALTH CHECK
    # ------------------------------------------------


    content.append(

        Spacer(
            1,
            20
        )

    )



    content.append(

        Paragraph(

            "Network Health Assessment",

            styles["Heading2"]

        )

    )



    health = "GOOD"



    if summary["fleet_uptime_pct"] < 95:

        health = "WARNING"



    if summary["total_outages"] > 5:

        health = "CRITICAL"




    content.append(

        Paragraph(

            f"Overall Network Health: {health}",

            styles["Normal"]

        )

    )





    content.append(

        PageBreak()

    )





    # ------------------------------------------------
    # HOST TABLE
    # ------------------------------------------------


    content.append(

        Paragraph(

            "Host Reliability",

            styles["Heading2"]

        )

    )




    host_data = [

        [

            "Host",
            "Status",
            "Uptime",
            "Latency",
            "Grade",
            "Outages"

        ]

    ]





    for ip,host in report["hosts"].items():


        host_data.append(

            [

                host["name"],


                "DOWN"
                if host["currently_down"]
                else "ONLINE",


                f'{host["uptime_pct"]}%',


                (
                    f'{host["avg_latency_ms"]} ms'
                    if host["avg_latency_ms"]
                    else "N/A"
                ),


                host["reliability_grade"],


                host["outage_count"]

            ]

        )





    host_table = Table(

        host_data,

        repeatRows=1

    )



    host_table.setStyle(

        TableStyle(

            [

                (

                    "GRID",

                    (0,0),

                    (-1,-1),

                    0.5,

                    None

                )

            ]

        )

    )



    content.append(

        host_table

    )







    # ------------------------------------------------
    # CHARTS
    # ------------------------------------------------


    content.append(

        PageBreak()

    )


    content.append(

        Paragraph(

            "Performance Charts",

            styles["Heading2"]

        )

    )




    for ip,host in report["hosts"].items():


        content.append(

            Paragraph(

                host["name"],

                styles["Heading3"]

            )

        )



        latency = create_latency_chart(host)



        if latency:


            content.append(

                Image(

                    latency,

                    width=400,

                    height=180

                )

            )





        loss = create_loss_chart(host)



        if loss:


            content.append(

                Image(

                    loss,

                    width=400,

                    height=180

                )

            )



        content.append(

            Spacer(
                1,
                20
            )

        )







    # ------------------------------------------------
    # OUTAGES
    # ------------------------------------------------


    content.append(

        PageBreak()

    )



    content.append(

        Paragraph(

            "Outage History",

            styles["Heading2"]

        )

    )



    outage_rows = [

        [

            "Host",

            "Start",

            "Duration"

        ]

    ]




    for outage in report.get(
        "outage_log",
        []
    ):


        outage_rows.append(

            [

                outage.get(
                    "host",
                    "Unknown"
                ),


                outage["start_time"],


                f'{outage["duration_seconds"]} seconds'

            ]

        )




    if len(outage_rows) == 1:


        outage_rows.append(

            [

                "No outages recorded",

                "",

                ""

            ]

        )





    outage_table = Table(

        outage_rows

    )



    outage_table.setStyle(

        TableStyle(

            [

                (

                    "GRID",

                    (0,0),

                    (-1,-1),

                    0.5,

                    None

                )

            ]

        )

    )



    content.append(

        outage_table

    )





    content.append(

        Spacer(
            1,
            30
        )

    )



    content.append(

        Paragraph(

            "Generated by Network Monitoring System",

            styles["Normal"]

        )

    )




    document.build(

        content,

        onFirstPage=add_page_number,

        onLaterPages=add_page_number

    )



    buffer.seek(0)



    return buffer