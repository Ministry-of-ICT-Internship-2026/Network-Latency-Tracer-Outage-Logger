import { useState } from "react";
import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";


export default function FleetTable({

    hosts = [],

    analytics = {},

    onDelete,

    onToggle

}) {


    const [search,setSearch] = useState("");





    function getHostStatus(ip){


        const data = analytics[ip];



        if(!data){


            return {


                status:"Unknown",

                latency:null,

                lastSeen:null


            };


        }





        return {


            status:

                data.currently_down

                ?

                "Offline"

                :

                "Online",


            latency:data.avg_latency_ms,


            lastSeen:data.last_seen


        };


    }






    const filteredHosts = hosts.filter(host => {


        const value = search.toLowerCase();



        return (

            host.hostname
            .toLowerCase()
            .includes(value)

            ||

            host.ip_address
            .toLowerCase()
            .includes(value)

        );


    });






    function removeHost(id){


        const confirmDelete =
            window.confirm(
                "Remove this host?"
            );


        if(confirmDelete){

            onDelete(id);

        }

    }






    return (


        <div className="host-table">





            <input

                className="host-search"

                placeholder="Search hostname or IP..."

                value={search}

                onChange={
                    e =>
                    setSearch(
                        e.target.value
                    )
                }

            />







            <table>



                <thead>

                    <tr>

                        <th>
                            Host
                        </th>

                        <th>
                            IP Address
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Latency
                        </th>

                        <th>
                            Monitoring
                        </th>

                        <th>
                            Last Checked
                        </th>

                        <th>
                            Created
                        </th>

                        <th>
                            Actions
                        </th>


                    </tr>


                </thead>







                <tbody>



                {

                filteredHosts.length === 0

                ?

                (

                <tr>

                    <td colSpan="8">

                        No hosts found

                    </td>

                </tr>

                )


                :


                filteredHosts.map(host => {



                    const status =
                        getHostStatus(
                            host.ip_address
                        );




                    return (


                    <tr key={host.id}>



                        <td>


                            <Link

                                to={`/hosts/${host.ip_address}`}

                            >

                                {host.hostname}

                            </Link>


                        </td>






                        <td>

                            {host.ip_address}

                        </td>






                        <td>


                        {


                        status.status === "Online"

                        &&


                        <span className="status-enabled">

                            Online

                        </span>


                        }



                        {


                        status.status === "Offline"

                        &&


                        <span className="status-disabled">

                            Offline

                        </span>


                        }



                        {


                        status.status === "Unknown"

                        &&


                        <span className="status-unknown">

                            Unknown

                        </span>


                        }


                        </td>







                        <td>


                        {


                        status.latency !== null

                        ?

                        `${status.latency.toFixed(2)} ms`

                        :

                        "N/A"


                        }


                        </td>







                        <td>


                            <StatusBadge

                                enabled={
                                    host.enabled
                                }

                            />


                        </td>








                        <td>


                        {


                        status.lastSeen

                        ?

                        new Date(
                            status.lastSeen
                        )
                        .toLocaleString()


                        :

                        "No data"


                        }


                        </td>







                        <td>


                            {
                                new Date(
                                    host.created_at
                                )
                                .toLocaleString()
                            }


                        </td>







                        <td>

                            <div className="host-actions">

                                <button
                                    className="toggle-btn"
                                    onClick={() =>
                                        onToggle(host.id)
                                        }
                                    >
                                    Toggle
                                </button>


                                <button
                                    className="delete-btn"
                                    onClick={() =>
                                        removeHost(host.id)
                                    }
                                >
                                    Delete
                                </button>

                            </div>

                        </td>




                    </tr>


                    );


                })


                }


                </tbody>



            </table>


        </div>


    );

}