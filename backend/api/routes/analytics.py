from fastapi import APIRouter
from fastapi import HTTPException

from monitoring.analytics import MonitoringAnalytics


router = APIRouter()



@router.get("/summary")
def dashboard_summary():

    analytics = MonitoringAnalytics()


    report = analytics.build_full_report()


    summary = report["summary"]


    online_hosts = (
        summary["hosts_monitored"]
        -
        len(summary["currently_down_hosts"])
    )


    return {

        "total_hosts": summary["hosts_monitored"],

        "online_hosts": online_hosts,

        "active_outages": len(
            summary["currently_down_hosts"]
        ),

        "avg_latency_ms": (
            summary["fleet_avg_latency_ms"]
            or 0
        ),

        "uptime_pct": summary["fleet_uptime_pct"],

        "total_outages": summary["total_outages"],

        "currently_down_hosts":
            summary["currently_down_hosts"]

    }

@router.get("/full")
def full_report():

    analytics = MonitoringAnalytics()


    return analytics.build_full_report()

@router.get("/host/{host_ip}")
def host_details(host_ip: str):

    analytics = MonitoringAnalytics()


    report = analytics.build_full_report()


    if host_ip not in report["hosts"]:

        raise HTTPException(
            status_code=404,
            detail="Host not found"
        )


    return report["hosts"][host_ip]