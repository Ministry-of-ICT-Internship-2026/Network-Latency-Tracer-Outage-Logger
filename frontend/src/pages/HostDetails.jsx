import { useParams } from "react-router-dom";

import useHostDetails from "../hooks/useHostDetails";

import LatencyChart from "../components/dashboard/LatencyChart";
import PacketLossChart from "../components/dashboard/PacketLossChart";

import "../styles/dashboard.css";


export default function HostDetails(){


    const { ip } = useParams();



    const {
        host,
        loading,
        error
    } = useHostDetails(ip);




    if(loading){

        return <h2>Loading host...</h2>;

    }



    if(error){

        return <h2>{error}</h2>;

    }



    if(!host){

        return <h2>No host data available.</h2>;

    }




    return (

        <div className="host-page">



            <h1>
                {host.display_name || host.name}
            </h1>



            <p className="host-ip">
                {ip}
            </p>





            {/* SUMMARY CARDS */}

            <div className="summary-grid">



                <div className="summary-card">

                    <h3>
                        Status
                    </h3>


                    <p>

                        {
                            host.currently_down

                            ?

                            "🔴 Down"

                            :

                            "🟢 Online"

                        }

                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Uptime
                    </h3>


                    <p>
                        {host.uptime_pct}%
                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Average Latency
                    </h3>


                    <p>

                        {
                            host.avg_latency_ms ?? "N/A"
                        }

                        ms

                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Reliability
                    </h3>


                    <p>
                        {host.reliability_grade}
                    </p>

                </div>




            </div>







            {/* EXTRA METRICS */}


            <div className="summary-grid">



                <div className="summary-card">

                    <h3>
                        Total Outages
                    </h3>


                    <p>
                        {host.outage_count}
                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Total Downtime
                    </h3>


                    <p>

                        {
                            Math.round(
                                host.total_downtime_seconds / 60
                            )
                        }

                        min

                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Failed Pings
                    </h3>


                    <p>
                        {host.failed_pings}
                    </p>

                </div>





                <div className="summary-card">

                    <h3>
                        Average Jitter
                    </h3>


                    <p>

                        {
                            host.avg_jitter_ms ?? "N/A"
                        }

                        ms

                    </p>

                </div>




            </div>









            {/* LATENCY CHART */}


            <div className="chart-card">


                <h2>
                    Latency History
                </h2>



                <LatencyChart

                    series={
                        host.latency_series || []
                    }

                />


            </div>









            {/* PACKET LOSS CHART */}


            <div className="chart-card">


                <h2>
                    Packet Loss
                </h2>



                <PacketLossChart

                    series={
                        host.loss_series || []
                    }

                />


            </div>









            {/* NETWORK STATISTICS */}



            <div className="table-card">


                <h2>
                    Network Statistics
                </h2>




                <table>


                    <tbody>


                        <tr>

                            <td>
                                Minimum Latency
                            </td>

                            <td>
                                {
                                    host.min_latency_ms ?? "N/A"
                                }
                                ms
                            </td>

                        </tr>





                        <tr>

                            <td>
                                Maximum Latency
                            </td>


                            <td>

                                {
                                    host.max_latency_ms ?? "N/A"
                                }

                                ms

                            </td>


                        </tr>





                        <tr>

                            <td>
                                P95 Latency
                            </td>


                            <td>

                                {
                                    host.p95_latency_ms ?? "N/A"
                                }

                                ms

                            </td>

                        </tr>





                        <tr>

                            <td>
                                Successful Pings
                            </td>


                            <td>
                                {host.successful_pings}
                            </td>

                        </tr>





                        <tr>

                            <td>
                                Failed Pings
                            </td>


                            <td>
                                {host.failed_pings}
                            </td>

                        </tr>



                    </tbody>


                </table>


            </div>









            {/* OUTAGE HISTORY */}



            <div className="table-card">


                <h2>
                    Outage History
                </h2>



                {

                    host.outages.length === 0

                    ?

                    <p>
                        No outages recorded.
                    </p>


                    :



                    <table>


                        <thead>

                            <tr>

                                <th>
                                    Start
                                </th>


                                <th>
                                    End
                                </th>


                                <th>
                                    Duration
                                </th>


                            </tr>


                        </thead>





                        <tbody>


                        {

                            host.outages.map(
                                (outage,index)=>(


                                <tr key={index}>


                                    <td>
                                        {outage.start_time}
                                    </td>



                                    <td>

                                        {
                                            outage.end_time
                                            ??
                                            "Still ongoing"
                                        }

                                    </td>



                                    <td>

                                        {
                                            Math.round(
                                                outage.duration_seconds / 60
                                            )
                                        }

                                        minutes

                                    </td>



                                </tr>


                            ))

                        }


                        </tbody>


                    </table>


                }



            </div>






        </div>


    );

}