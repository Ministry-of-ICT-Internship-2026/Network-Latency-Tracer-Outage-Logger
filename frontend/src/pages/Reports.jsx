import { useState } from "react";

import useReports from "../hooks/useReports";

import ReportButton from "../components/reports/ReportButton";

import "../styles/reports.css";


export default function Reports() {


    const {
        report,
        loading,
        error
    } = useReports();



    const [format, setFormat] =
        useState("pdf");




    if (loading) {

        return (
            <h2>
                Loading reports...
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
                Generate the full network monitoring report.
            </p>





            {/* Report Generator */}

            <div className="report-section">


                <h2>
                    Generate Report
                </h2>



                <div className="report-generator-card">



                    <label>
                        Output Format
                    </label>



                    <select

                        value={format}

                        onChange={
                            e =>
                            setFormat(
                                e.target.value
                            )
                        }

                    >

                        <option value="pdf">
                            PDF
                        </option>


                        <option value="csv">
                            CSV
                        </option>


                    </select>





                    <ReportButton

                        format={format}

                        label="Generate Report"

                    />



                </div>


            </div>








            {/* Summary */}

            {
                report && (

                    <div className="report-section">


                        <h2>
                            Latest Network Summary
                        </h2>



                        <div className="report-grid">



                            <div className="report-card">

                                <h3>
                                    Hosts Monitored
                                </h3>

                                <p>
                                    {
                                    report.summary.hosts_monitored
                                    }
                                </p>

                            </div>





                            <div className="report-card">

                                <h3>
                                    Fleet Uptime
                                </h3>

                                <p>
                                    {
                                    report.summary.fleet_uptime_pct
                                    }%
                                </p>

                            </div>






                            <div className="report-card">

                                <h3>
                                    Average Latency
                                </h3>

                                <p>
                                    {
                                    report.summary.fleet_avg_latency_ms
                                    } ms
                                </p>

                            </div>






                            <div className="report-card">

                                <h3>
                                    Total Outages
                                </h3>

                                <p>
                                    {
                                    report.summary.total_outages
                                    }
                                </p>

                            </div>





                            <div className="report-card">

                                <h3>
                                    Downtime
                                </h3>

                                <p>
                                    {
                                    report.summary.total_downtime_human
                                    }
                                </p>

                            </div>



                        </div>


                    </div>

                )

            }



        </div>

    );

}
