import useFleet from "../hooks/useFleet";

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



    if(loading){

        return <h2>Loading fleet...</h2>;

    }



    if(error){

        return <h2>{error}</h2>;

    }



    return (

        <div className="host-page">


            <h1>
                Fleet Monitoring
            </h1>




            <HostForm

                onAdd={addHost}

            />





            <FleetTable

                hosts={hosts}

                onDelete={deleteHost}

                onToggle={toggleHost}

            />



        </div>

    );

}