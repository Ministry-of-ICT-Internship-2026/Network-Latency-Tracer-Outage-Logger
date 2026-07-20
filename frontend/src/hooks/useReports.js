import {
    useEffect,
    useState
} from "react";


import api from "../services/api";



export default function useReports(){


    const [report,setReport] = useState(null);

    const [loading,setLoading] = useState(true);

    const [error,setError] = useState(null);



    useEffect(()=>{


        async function loadReport(){


            try{


                const response =
                    await api.get(
                        "/reports/"
                    );


                setReport(
                    response.data
                );


            }
            catch(err){

                setError(
                    err.message
                );

            }
            finally{

                setLoading(false);

            }


        }


        loadReport();


    },[]);



    return {
        report,
        loading,
        error
    };

}