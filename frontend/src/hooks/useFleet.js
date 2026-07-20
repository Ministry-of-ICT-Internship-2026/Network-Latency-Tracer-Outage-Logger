import { useEffect, useState } from "react";
import api from "../services/api";


export default function useFleet(){


    const [hosts,setHosts] = useState([]);

    const [loading,setLoading] = useState(true);

    const [error,setError] = useState(null);



    async function fetchHosts(showLoading=true){


        try{


            if(showLoading)
                setLoading(true);


            setError(null);



            const response = await api.get(
                "/hosts"
            );


            setHosts(
                response.data
            );


        }


        catch(err){


            console.error(
                "Fleet error:",
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

        fetchHosts();

    },[]);





    async function addHost(host){


        try{


            setError(null);


            await api.post(
                "/hosts",
                host
            );


            await fetchHosts(false);


        }

        catch(err){

            setError(err.message);

        }

    }





    async function deleteHost(id){


        try{


            setError(null);


            await api.delete(
                `/hosts/${id}`
            );


            await fetchHosts(false);


        }

        catch(err){

            setError(err.message);

        }

    }





    async function toggleHost(id){


        try{


            setError(null);


            await api.patch(
                `/hosts/${id}/toggle`
            );


            await fetchHosts(false);


        }

        catch(err){

            setError(err.message);

        }

    }





    return {

        hosts,

        loading,

        error,

        refreshHosts: fetchHosts,

        addHost,

        deleteHost,

        toggleHost

    };


}