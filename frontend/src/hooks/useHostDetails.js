import { useEffect, useState } from "react";
import api from "../services/api";


export default function useHostDetails(ip){


    const [host, setHost] = useState(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState(null);



    useEffect(() => {


        if(!ip){

            setLoading(false);

            return;

        }



        async function loadHost(){


            try {


                setLoading(true);

                setError(null);

                setHost(null);



                const response = await api.get(

                    `/analytics/host/${encodeURIComponent(ip)}`

                );



                setHost(
                    response.data
                );


            }


            catch(err){


                console.error(
                    "Host details error:",
                    err
                );


                setError(

                    err.response?.data?.detail
                    ||
                    err.message

                );


            }


            finally{


                setLoading(false);


            }


        }



        loadHost();



    },[ip]);




    return {

        host,

        loading,

        error

    };


}