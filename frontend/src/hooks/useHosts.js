import { useEffect, useState } from "react";
import {
    getHosts,
    addHost,
    deleteHost,
    toggleHost
} from "../services/api";


export default function useHosts(){

    const [hosts,setHosts] = useState([]);

    const [loading,setLoading] = useState(true);

    const [error,setError] = useState(null);



    async function fetchHosts(){

        try{

            const data = await getHosts();

            setHosts(data);

        }
        catch(err){

            setError(err.message);

        }
        finally{

            setLoading(false);

        }

    }



    useEffect(()=>{

        fetchHosts();

    },[]);



    async function removeHost(id){

        await deleteHost(id);

        fetchHosts();

    }



    async function toggleHost(id){

        await toggleHost(id);

        fetchHosts();

    }



    async function createHost(host){

        await addHost(host);

        fetchHosts();

    }



    return {

        hosts,
        loading,
        error,

        createHost,
        removeHost,
        toggleHost

    };

}