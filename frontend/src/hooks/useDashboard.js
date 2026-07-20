import { useEffect, useState } from "react";
import api from "../services/api";


export default function useDashboard(){


    const [dashboard, setDashboard] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);



    async function fetchDashboard(){


        try {


            const response = await api.get(
                "/analytics/full"
            );


            setDashboard(
                response.data
            );


        }
        catch(err){


            console.error(
                "Dashboard error:",
                err
            );


            setError(
                err.message
            );


        }
        finally{


            setLoading(false);


        }


    }



    useEffect(()=>{


        fetchDashboard();


    },[]);



    return {

        dashboard,

        loading,

        error

    };


}