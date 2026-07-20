import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";


export default function FleetTable({
    hosts = [],
    onDelete,
    onToggle
}) {


    return (

        <div className="host-table">


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
                            Monitoring
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
                        hosts.map(host => (


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

                                    <StatusBadge
                                        enabled={host.enabled}
                                    />

                                </td>



                                <td>

                                    {
                                        new Date(
                                            host.created_at
                                        ).toLocaleString()
                                    }

                                </td>



                                <td>


                                    <button
                                        onClick={() =>
                                            onToggle(host.id)
                                        }
                                    >

                                        Toggle

                                    </button>




                                    <button
                                        onClick={() =>
                                            onDelete(host.id)
                                        }
                                    >

                                        Delete

                                    </button>


                                </td>


                            </tr>


                        ))
                    }


                </tbody>


            </table>


        </div>

    );

}