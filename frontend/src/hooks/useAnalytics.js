import { useEffect, useState } from "react";
import api from "../services/api";


export default function useAnalytics(){


    const [analytics,setAnalytics] = useState({});

    const [loading,setLoading] = useState(true);

    const [error,setError] = useState(null);



    async function fetchAnalytics(){

        try{

            setError(null);


            const response = await api.get(
                "/analytics/full"
            );


            console.log(
                "Analytics:",
                response.data
            );


            setAnalytics(
                response.data.hosts ?? {}
            );


        }


        catch(err){

            console.error(
                "Analytics error:",
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


        fetchAnalytics();


        const timer = setInterval(
            fetchAnalytics,
            10000
        );


        return ()=>clearInterval(timer);


    },[]);



    return {

        analytics,

        loading,

        error,

        refreshAnalytics:fetchAnalytics

    };

}