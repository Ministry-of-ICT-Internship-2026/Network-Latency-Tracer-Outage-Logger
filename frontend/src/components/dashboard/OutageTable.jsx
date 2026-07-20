export default function OutageTable({ outages = [] }) {


    if (outages.length === 0) {

        return (

            <div className="table-card">

                <h3>
                    Recent Outages
                </h3>

                <p>
                    No outages recorded.
                </p>

            </div>

        );

    }



    return (

        <div className="table-card">


            <h3>
                Recent Outages
            </h3>



            <table className="outage-table">


                <thead>

                    <tr>

                        <th>
                            Host
                        </th>

                        <th>
                            Start Time
                        </th>

                        <th>
                            Duration
                        </th>

                        <th>
                            Status
                        </th>

                    </tr>

                </thead>



                <tbody>


                    {outages.map((outage, index) => (


                        <tr key={index}>


                            <td>
                                {outage.display_name || outage.host}
                            </td>



                            <td>

                                {new Date(
                                    outage.start_time
                                ).toLocaleString()}

                            </td>



                            <td>

                                {Math.round(
                                    outage.duration_seconds / 60
                                )}

                                {" "}minutes

                            </td>



                            <td>


                                {
                                    outage.ongoing

                                    ?

                                    <span className="status-down">
                                        🔴 Ongoing
                                    </span>

                                    :

                                    <span className="status-recovered">
                                        🟢 Recovered
                                    </span>

                                }


                            </td>


                        </tr>


                    ))}


                </tbody>


            </table>


        </div>

    );

}