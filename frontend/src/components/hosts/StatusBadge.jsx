export default function StatusBadge({enabled}){


    return (

        <span
            className={
                enabled
                ?
                "status-enabled"
                :
                "status-disabled"
            }
        >

            {
                enabled
                ?
                "Enabled"
                :
                "Disabled"
            }

        </span>

    );

}