import useFleet from "../hooks/useFleet";
import useAnalytics from "../hooks/useAnalytics";

import FleetTable from "../components/hosts/FleetTable";
import HostForm from "../components/hosts/HostForm";

import "../styles/hosts.css";


export default function Fleet(){


    const {

        hosts,

        loading,

        error,

        addHost,

        deleteHost,

        toggleHost

    } = useFleet();



    const {

        analytics,

        loading: analyticsLoading,

        error: analyticsError

    } = useAnalytics();




    if(loading || analyticsLoading){

        return (

            <div className="loading">

                Loading fleet...

            </div>

        );

    }




    if(error || analyticsError){

        return (

            <div className="empty-state">

                {error || analyticsError}

            </div>

        );

    }




    return (

        <div className="host-page">


            <div className="page-header">

                <h1>
                    Fleet Monitoring
                </h1>


                <p>
                    Monitor and manage your network hosts
                </p>

            </div>



            <HostForm

                onAdd={addHost}

            />



            <FleetTable

                hosts={hosts}

                analytics={analytics}

                onDelete={deleteHost}

                onToggle={toggleHost}

            />


        </div>

    );

}