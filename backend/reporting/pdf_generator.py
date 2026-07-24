import os
from io import BytesIO
from datetime import datetime, timezone


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
from reportlab.lib.colors import HexColor


from reporting.charts import (
    create_latency_chart,
    create_loss_chart
)




# ==================================================
# FORMATTING HELPERS
# ==================================================

def format_duration(seconds):
    """174820.8 -> '2d 0h 33m'. Falls back to the raw value if it
    isn't a plain number (e.g. already a string, or None)."""

    try:

        seconds = int(float(seconds))

    except (TypeError, ValueError):

        return seconds


    days, remainder = divmod(seconds, 86400)

    hours, remainder = divmod(remainder, 3600)

    minutes, _ = divmod(remainder, 60)


    parts = []


    if days:

        parts.append(f"{days}d")


    if hours or days:

        parts.append(f"{hours}h")


    parts.append(f"{minutes}m")


    return " ".join(parts)



def format_timestamp(raw):
    """ISO datetime string -> '24 Jul 2026 06:04'. Falls back to the
    raw value if it doesn't parse."""

    try:

        dt = datetime.fromisoformat(raw)

        return dt.strftime("%d %b %Y %H:%M")

    except (TypeError, ValueError):

        return raw



# Grade -> accent hex color. Unrecognized grades fall back to slate.
GRADE_COLORS = {

    "Excellent": "#15803d",

    "Good": "#2563eb",

    "Fair": "#b45309",

    "Poor": "#c2410c",

    "Critical": "#b91c1c"

}


STATUS_COLORS = {

    "ONLINE": "#15803d",

    "DOWN": "#b91c1c"

}



def colored_label(text, hex_color):

    return Paragraph(

        f'<font color="{hex_color}"><b>{text}</b></font>',

        getSampleStyleSheet()["Normal"]

    )




# ==================================================
# PAGE NUMBER
# ==================================================

def add_page_number(canvas, doc):

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        9
    )

    canvas.setFillColor(
        HexColor("#94a3b8")
    )

    canvas.drawString(
        40,
        20,
        f"Network Monitor Report - Page {doc.page}"
    )

    canvas.restoreState()




# ==================================================
# TABLE STYLE
# ==================================================

def make_table(data, col_widths=None):

    table = Table(
        data,
        repeatRows=1,
        hAlign="LEFT",
        colWidths=col_widths
    )


    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    HexColor("#1e293b")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    HexColor("#ffffff")
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0,0),
                    (-1,0),
                    9
                ),

                (
                    "ALIGN",
                    (0,0),
                    (-1,-1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0,0),
                    (-1,-1),
                    "MIDDLE"
                ),

                (
                    "LINEBELOW",
                    (0,0),
                    (-1,0),
                    1,
                    HexColor("#1e293b")
                ),

                (
                    "LINEBELOW",
                    (0,1),
                    (-1,-1),
                    0.5,
                    HexColor("#e2e8f0")
                ),

                (
                    "ROWBACKGROUNDS",
                    (0,1),
                    (-1,-1),
                    [
                        HexColor("#ffffff"),
                        HexColor("#f8fafc")
                    ]
                ),

                (
                    "FONTSIZE",
                    (0,1),
                    (-1,-1),
                    9
                ),

                (
                    "TEXTCOLOR",
                    (0,1),
                    (-1,-1),
                    HexColor("#334155")
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    9
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    9
                )

            ]

        )

    )


    return table




# ==================================================
# KPI CARDS
# ==================================================

def make_kpi_cards(items, styles):

    cards = []


    for title, value, accent_hex in items:


        title_para = Paragraph(

            f'<font color="#64748b">{title}</font>',

            styles["Normal"]

        )


        value_para = Paragraph(

            f'<font color="{accent_hex}"><b>{value}</b></font>',

            styles["Heading2"]

        )


        card = Table(

            [
                [title_para],
                [value_para]
            ],

            colWidths=[120],

            rowHeights=[
                22,
                34
            ]

        )


        card.setStyle(

            TableStyle(

                [

                    (
                        "BOX",
                        (0,0),
                        (-1,-1),
                        0.7,
                        HexColor("#e2e8f0")
                    ),

                    (
                        "LINEBELOW",
                        (0,0),
                        (-1,0),
                        2,
                        HexColor(accent_hex)
                    ),

                    (
                        "ALIGN",
                        (0,0),
                        (-1,-1),
                        "CENTER"
                    ),

                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "MIDDLE"
                    ),

                    (
                        "BACKGROUND",
                        (0,0),
                        (-1,-1),
                        HexColor("#f8fafc")
                    )

                ]

            )

        )


        cards.append(card)


    row1 = cards[:3]

    row2 = cards[3:]

    while len(row2) < len(row1):

        row2.append("")


    outer = Table(

        [
            row1,
            row2
        ],

        hAlign="LEFT"

    )


    outer.setStyle(

        TableStyle(

            [
                ("TOPPADDING", (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6)
            ]

        )

    )


    return outer




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

    styles["Title"].textColor = HexColor("#0f172a")

    styles["Heading2"].textColor = HexColor("#0f172a")

    styles["Heading3"].textColor = HexColor("#1e293b")



    content = []


    temp_chart_files = []



    generated = datetime.now(
        timezone.utc
    ).strftime(
        "%d %B %Y %H:%M UTC"
    )




    # ==================================================
    # COVER
    # ==================================================


    content.append(

        Paragraph(

            "Network Latency Tracer",

            styles["Title"]

        )

    )


    content.append(
        Spacer(1,16)
    )


    content.append(

        Paragraph(

            '<font color="#64748b">Full Reliability Report</font>',

            styles["Heading2"]

        )

    )


    content.append(

        Paragraph(

            f'<font color="#94a3b8">Generated: {generated}</font>',

            styles["Normal"]

        )

    )


    content.append(
        Spacer(1,40)
    )




    # ==================================================
    # SUMMARY
    # ==================================================


    summary = report.get(
        "summary",
        {}
    )



    content.append(

        Paragraph(

            "Executive Summary",

            styles["Heading2"]

        )

    )


    content.append(
        Spacer(1,10)
    )



    accent_blue = "#2563eb"

    accent_green = "#15803d"

    accent_amber = "#b45309"

    accent_red = "#b91c1c"

    accent_slate = "#334155"



    cards = make_kpi_cards(

        [

            (
                "HOSTS",
                summary.get("hosts_monitored", 0),
                accent_slate
            ),

            (
                "UPTIME",
                f'{summary.get("fleet_uptime_pct")}%',
                accent_green
            ),

            (
                "AVG LATENCY",
                f'{summary.get("fleet_avg_latency_ms")} ms',
                accent_blue
            ),

            (
                "OUTAGES",
                summary.get("total_outages", 0),
                accent_amber
            ),

            (
                "DOWNTIME",
                summary.get("total_downtime_human", "0s"),
                accent_red
            )

        ],

        styles

    )


    content.append(cards)


    content.append(
        Spacer(1,20)
    )




    # ==================================================
    # HOST RELIABILITY
    # ==================================================


    content.append(
        PageBreak()
    )


    content.append(

        Paragraph(

            "Host Reliability",

            styles["Heading2"]

        )

    )


    content.append(
        Spacer(1,10)
    )



    rows = [

        [
            "Host",
            "Status",
            "Uptime",
            "Latency",
            "Grade",
            "Outages"
        ]

    ]



    for ip, host in report.get(
        "hosts",
        {}
    ).items():


        status_text = (
            "DOWN"
            if host.get("currently_down")
            else "ONLINE"
        )


        grade_text = host.get(
            "reliability_grade",
            ""
        )


        status_cell = colored_label(
            status_text,
            STATUS_COLORS.get(
                status_text,
                "#334155"
            )
        )


        grade_cell = colored_label(
            grade_text,
            GRADE_COLORS.get(
                grade_text,
                "#334155"
            )
        )


        rows.append(

            [

                host.get(
                    "name",
                    ip
                ),

                status_cell,

                f'{host.get("uptime_pct")}%',

                host.get(
                    "avg_latency_ms"
                ),

                grade_cell,

                host.get(
                    "outage_count"
                )

            ]

        )


    content.append(
        make_table(rows)
    )




    # ==================================================
    # OUTAGE HISTORY
    # ==================================================


    content.append(
        PageBreak()
    )


    content.append(

        Paragraph(

            "Outage History",

            styles["Heading2"]

        )

    )


    content.append(
        Spacer(1,10)
    )


    outage_rows = [

        [
            "Host",
            "Start",
            "Duration"
        ]

    ]


    outage_log = report.get(
        "outage_log",
        []
    )


    if outage_log:

        for outage in outage_log:


            outage_rows.append(

                [

                    outage.get(
                        "host"
                    ),

                    format_timestamp(
                        outage.get("start_time")
                    ),

                    format_duration(
                        outage.get("duration_seconds")
                    )

                ]

            )


        content.append(

            make_table(

                outage_rows,

                col_widths=[160, 180, 100]

            )

        )


    else:


        content.append(

            Paragraph(

                '<font color="#64748b">No outages recorded.</font>',

                styles["Normal"]

            )

        )




    # ==================================================
    # CHARTS
    # ==================================================


    content.append(
        PageBreak()
    )


    content.append(

        Paragraph(

            "Performance Charts",

            styles["Heading2"]

        )

    )


    content.append(
        Spacer(1,10)
    )



    for ip, host in report.get(
        "hosts",
        {}
    ).items():


        content.append(

            Paragraph(

                host.get(
                    "name",
                    ip
                ),

                styles["Heading3"]

            )

        )


        content.append(
            Spacer(1,6)
        )



        latency = create_latency_chart(host)


        if latency:

            temp_chart_files.append(latency)

            content.append(

                Image(
                    latency,
                    width=400,
                    height=180
                )

            )



        loss = create_loss_chart(host)



        if loss:

            temp_chart_files.append(loss)

            content.append(

                Image(
                    loss,
                    width=400,
                    height=180
                )

            )


        content.append(
            Spacer(1,14)
        )




    # ==================================================
    # FOOTER
    # ==================================================


    content.append(
        Spacer(1,30)
    )


    content.append(

        Paragraph(

            '<font color="#94a3b8">Generated by Network Monitoring System</font>',

            styles["Normal"]

        )

    )



    document.build(

        content,

        onFirstPage=add_page_number,

        onLaterPages=add_page_number

    )


    for path in temp_chart_files:

        try:

            os.remove(path)

        except OSError:

            pass



    buffer.seek(0)


    return buffer