from fastapi import APIRouter
from fastapi.responses import Response
from fastapi.responses import StreamingResponse


from monitoring.analytics import MonitoringAnalytics

from reporting.csv_exporter import generate_csv
from reporting.pdf_generator import generate_pdf

router = APIRouter()



@router.get("/")
def get_report():

    analytics = MonitoringAnalytics()

    return analytics.build_full_report()




@router.get("/csv")
def export_csv():


    analytics = MonitoringAnalytics()


    report = analytics.build_full_report()



    csv_data = generate_csv(
        report
    )



    return Response(

        content=csv_data,

        media_type="text/csv",

        headers={
            "Content-Disposition":
            "attachment; filename=network_report.csv"
        }

    )

@router.get("/pdf")
def export_pdf():


    analytics = MonitoringAnalytics()


    report = analytics.build_full_report()


    pdf = generate_pdf(
        report
    )


    return StreamingResponse(

        pdf,

        media_type="application/pdf",

        headers={
            "Content-Disposition":
            "attachment; filename=network_reliability_report.pdf"
        }

    )