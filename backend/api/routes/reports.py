from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from monitoring.analytics import MonitoringAnalytics

from reporting.csv_exporter import generate_csv
from reporting.pdf_generator import generate_pdf

from reporting.report_types import ReportFormat


router = APIRouter()


@router.get("/")
def get_report():

    analytics = MonitoringAnalytics()

    return analytics.build_full_report()


@router.get("/generate")
def generate_report(

    output_format: ReportFormat = ReportFormat.PDF

):

    analytics = MonitoringAnalytics()

    try:

        report = analytics.build_full_report()

        if output_format == ReportFormat.CSV:

            csv_data = generate_csv(report)

            return Response(

                content=csv_data,

                media_type="text/csv",

                headers={

                    "Content-Disposition":

                    "attachment; filename=network_report.csv"

                }

            )

        pdf = generate_pdf(report)

        return Response(

            content=pdf.getvalue(),

            media_type="application/pdf",

            headers={

                "Content-Disposition":

                "attachment; filename=network_report.pdf"

            }

        )

    except HTTPException:

        raise

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            500,
            str(e)
        )