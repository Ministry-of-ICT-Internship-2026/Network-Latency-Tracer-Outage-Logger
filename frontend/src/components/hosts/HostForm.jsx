import { useState } from "react";


export default function HostForm({ onAdd }){


    const [hostname,setHostname] = useState("");

    const [ip,setIp] = useState("");



    function submit(e){


        e.preventDefault();



        if(!hostname || !ip){

            return;

        }



        onAdd({

            hostname,

            ip_address: ip

        });



        setHostname("");

        setIp("");

    }





    return (

        <form
            onSubmit={submit}
            className="host-form"
        >


            <h3>
                Add Host
            </h3>



            <input

                type="text"

                placeholder="Hostname"

                value={hostname}

                onChange={
                    e => setHostname(e.target.value)
                }

            />



            <input

                type="text"

                placeholder="IP Address"

                value={ip}

                onChange={
                    e => setIp(e.target.value)
                }

            />



            <button
                type="submit"
            >

                Add Host

            </button>


        </form>

    );

}