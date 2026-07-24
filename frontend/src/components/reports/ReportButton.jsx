import api from "../../services/api";


export default function ReportButton({
    format,
    label
}) {


    async function downloadReport(){


        try {


            const params = new URLSearchParams();


            params.append(
                "output_format",
                format
            );



            const response = await api.get(

                `/reports/generate?${params.toString()}`,

                {
                    responseType: "blob"
                }

            );



            const contentType =
                format === "pdf"
                ?
                "application/pdf"
                :
                "text/csv";



            const blob = new Blob(

                [
                    response.data
                ],

                {
                    type: contentType
                }

            );



            const url =
                window.URL.createObjectURL(blob);



            const link =
                document.createElement("a");



            link.href = url;



            link.download =
                `network_report.${format}`;



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
