import useReports from "../hooks/useReports";

import ReportButton from "../components/reports/ReportButton";

import "../styles/reports.css";


export default function Reports() {


    const {
        report,
        loading,
        error
    } = useReports();



    if (loading) {

        return (
            <h2>
                Generating report...
            </h2>
        );

    }



    if (error) {

        return (
            <h2>
                {error}
            </h2>
        );

    }



    return (

        <div className="reports-page">


            <h1>
                Reports
            </h1>



            <p>
                Generate and download network monitoring reports.
            </p>





            {/* Export Section */}

            <div className="report-section">


                <h2>
                    Export Reports
                </h2>



                <div className="report-grid">



                    <div className="report-card">


                        <h3>
                            CSV Report
                        </h3>


                        <p>
                            Export monitoring data
                        </p>



                        <ReportButton

                            type="csv"

                            label="Download CSV"

                        />


                    </div>






                    <div className="report-card">


                        <h3>
                            PDF Report
                        </h3>


                        <p>
                            Printable network report
                        </p>



                        <ReportButton

                            type="pdf"

                            label="Download PDF"

                        />


                    </div>




                </div>


            </div>







            {/* Summary Section */}

            {
                report && (

                    <div className="report-section">


                        <h2>
                            Latest Report Summary
                        </h2>



                        <div className="report-grid">



                            <div className="report-card">

                                <h3>
                                    Hosts Monitored
                                </h3>

                                <p>
                                    {report.summary.hosts_monitored}
                                </p>

                            </div>





                            <div className="report-card">

                                <h3>
                                    Fleet Uptime
                                </h3>

                                <p>
                                    {report.summary.fleet_uptime_pct}%
                                </p>

                            </div>






                            <div className="report-card">

                                <h3>
                                    Average Latency
                                </h3>

                                <p>
                                    {report.summary.fleet_avg_latency_ms}
                                    ms
                                </p>

                            </div>






                            <div className="report-card">

                                <h3>
                                    Total Outages
                                </h3>

                                <p>
                                    {report.summary.total_outages}
                                </p>

                            </div>






                            <div className="report-card">

                                <h3>
                                    Downtime
                                </h3>

                                <p>
                                    {report.summary.total_downtime_human}
                                </p>

                            </div>



                        </div>


                    </div>

                )
            }



        </div>

    );

}