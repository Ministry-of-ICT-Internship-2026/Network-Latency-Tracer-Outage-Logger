import {
    Line
} from "react-chartjs-2";


export default function LatencyChart({ series = [] }) {


    const data = {

        labels: series.map(
            item => item.t
        ),


        datasets: [

            {
                label: "Latency (ms)",

                data: series.map(
                    item => item.avg_ms
                ),


                borderColor: "#2563eb",

                backgroundColor: "rgba(37, 99, 235, 0.2)",


                borderWidth: 3,


                tension: 0.3,


                pointRadius: 4,

                pointBackgroundColor: "#2563eb"

            }

        ]

    };



    const options = {


        responsive: true,


        maintainAspectRatio: false,


        plugins: {

            legend: {

                display: true,

                labels: {

                    color: "#333"

                }

            }

        },


        scales: {


            x: {

                ticks: {

                    color: "#555"

                },

                grid: {

                    color: "#e5e7eb"

                }

            },


            y: {

                ticks: {

                    color: "#555"

                },

                grid: {

                    color: "#e5e7eb"

                },

                beginAtZero: true

            }


        }


    };



    return (

        <div style={{height:"300px"}}>

            <Line

                data={data}

                options={options}

            />

        </div>

    );

}