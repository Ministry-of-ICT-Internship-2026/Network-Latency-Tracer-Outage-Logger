import { useState } from "react";


export default function HostForm({ onAdd }){


    const [hostname,setHostname] = useState("");

    const [ip,setIp] = useState("");

    const [error,setError] = useState("");

    const [loading,setLoading] = useState(false);





    function validateIP(address){


        const regex =
        /^(\d{1,3}\.){3}\d{1,3}$/;


        return regex.test(address);

    }






    async function submit(e){


        e.preventDefault();



        setError("");




        if(!hostname.trim() || !ip.trim()){


            setError(
                "Hostname and IP address are required"
            );

            return;

        }





        if(!validateIP(ip)){


            setError(
                "Enter a valid IPv4 address"
            );

            return;

        }





        try{


            setLoading(true);



            await onAdd({

                hostname: hostname.trim(),

                ip_address: ip.trim()

            });



            setHostname("");

            setIp("");



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






    return (


        <form

            onSubmit={submit}

            className="host-form"

        >



            <h3>
                Add New Host
            </h3>





            {
                error && (

                    <p className="form-error">

                        {error}

                    </p>

                )
            }







            <input


                type="text"


                placeholder="Host name e.g Google DNS"


                value={hostname}


                onChange={

                    e =>
                    setHostname(
                        e.target.value
                    )

                }


            />






            <input


                type="text"


                placeholder="IP address e.g 8.8.8.8"


                value={ip}


                onChange={

                    e =>
                    setIp(
                        e.target.value
                    )

                }


            />







            <button

                type="submit"

                disabled={loading}

            >


                {
                    loading

                    ?

                    "Adding..."

                    :

                    "Add Host"

                }


            </button>





        </form>


    );

}