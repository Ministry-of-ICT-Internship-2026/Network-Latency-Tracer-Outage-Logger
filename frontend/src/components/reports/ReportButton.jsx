import api from "../../services/api";


export default function ReportButton({
    type,
    label
}) {


    async function downloadReport(){


        try {


            const response = await api.get(

                `/reports/${type}`,

                {
                    responseType: "blob"
                }

            );



            const contentType =
                type === "pdf"
                ?
                "application/pdf"
                :
                "text/csv";



            const blob = new Blob(

                [response.data],

                {
                    type: contentType
                }

            );



            const url =
                window.URL.createObjectURL(blob);



            const link =
                document.createElement("a");



            link.href = url;



            link.setAttribute(

                "download",

                `network_report.${type}`

            );



            document.body.appendChild(link);



            link.click();



            document.body.removeChild(link);



            window.URL.revokeObjectURL(url);



        }
        catch(error){


            console.error(
                "Report download failed:",
                error.response || error
            );


        }


    }



    return (

        <button
            onClick={downloadReport}
        >

            {label}

        </button>

    );

}