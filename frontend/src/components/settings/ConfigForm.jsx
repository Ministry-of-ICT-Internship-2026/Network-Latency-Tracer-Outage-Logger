export default function ConfigForm(){

    return (

        <>

            <label>
                Monitoring Interval (seconds)
            </label>


            <input
                type="number"
                defaultValue="5"
                readOnly
            />



            <label>
                Ping Timeout (seconds)
            </label>


            <input
                type="number"
                defaultValue="2"
                readOnly
            />



            <label>
                Failure Threshold
            </label>


            <input
                type="number"
                defaultValue="3"
                readOnly
            />



            <button>
                Save Changes
            </button>


        </>

    );

}