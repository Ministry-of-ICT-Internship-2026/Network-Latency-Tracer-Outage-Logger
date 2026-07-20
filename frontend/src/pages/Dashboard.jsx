import { useState } from "react";

import useDashboard from "../hooks/useDashboard";

import SummaryCard from "../components/dashboard/SummaryCard";
import LatencyChart from "../components/dashboard/LatencyChart";
import PacketLossChart from "../components/dashboard/PacketLossChart";
import OutageTable from "../components/dashboard/OutageTable";

import "../styles/dashboard.css";


export default function Dashboard(){


    const {
        dashboard,
        loading,
        error
    } = useDashboard();



    const [selectedHost, setSelectedHost] = useState("");



    if(loading){

        return <h2>Loading dashboard...</h2>;

    }



    if(error){

        return <h2>{error}</h2>;

    }



    if(!dashboard){

        return <h2>No dashboard data</h2>;

    }



    const summary = dashboard.summary;

    const hosts = dashboard.hosts || {};

    const hostKeys = Object.keys(hosts);



    if(hostKeys.length === 0){

        return <h2>No hosts available</h2>;

    }



    const activeHost = selectedHost || hostKeys[0];

    const hostData = hosts[activeHost];



    return (

        <div className="dashboard-page">


            <h1>
                Network Dashboard
            </h1>



            {/* SUMMARY */}

            <div className="summary-grid">


                <SummaryCard
                    title="Hosts"
                    value={summary.hosts_monitored}
                />


                <SummaryCard
                    title="Fleet Uptime"
                    value={`${summary.fleet_uptime_pct}%`}
                />


                <SummaryCard
                    title="Average Latency"
                    value={`${summary.fleet_avg_latency_ms} ms`}
                />


                <SummaryCard
                    title="Total Outages"
                    value={summary.total_outages}
                />


                <SummaryCard
                    title="Downtime"
                    value={summary.total_downtime_human}
                />


            </div>





            {/* STATUS */}

            <div className="status-box">


                <h2>
                    Current Status
                </h2>


                {
                    summary.currently_down_hosts.length > 0

                    ?

                    <p className="status-down">

                        🔴 Down:
                        {" "}
                        {
                            summary.currently_down_hosts.join(", ")
                        }

                    </p>

                    :

                    <p className="status-ok">

                        🟢 All systems operational

                    </p>

                }


            </div>







            {/* PERFORMANCE */}


            <div className="dashboard-section">


                <h2>
                    Performance Monitoring
                </h2>



                <div className="host-selector">


                    <select

                        value={activeHost}

                        onChange={(e)=>
                            setSelectedHost(
                                e.target.value
                            )
                        }

                    >


                        {
                            hostKeys.map(host => (

                                <option
                                    key={host}
                                    value={host}
                                >

                                    {
                                        hosts[host].display_name
                                    }

                                </option>

                            ))
                        }


                    </select>


                </div>





                <div className="chart-card">


                    <h3>
                        Latency Trend
                    </h3>


                    <LatencyChart

                        series={
                            hostData?.latency_series || []
                        }

                    />


                </div>






                <div className="chart-card">


                    <h3>
                        Packet Loss
                    </h3>


                    <PacketLossChart

                        series={
                            hostData?.loss_series || []
                        }

                    />


                </div>


            </div>







            {/* OUTAGES */}


            <div className="table-card">


                <h2>
                    Outage History
                </h2>



                <OutageTable

                    outages={
                        dashboard.outage_log
                    }

                />


            </div>



        </div>

    );

}