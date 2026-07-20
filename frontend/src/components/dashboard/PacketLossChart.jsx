import {

    Chart as ChartJS,

    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend

} from "chart.js";

import { Line } from "react-chartjs-2";


ChartJS.register(

    CategoryScale,

    LinearScale,

    PointElement,

    LineElement,

    Tooltip,

    Legend

);


export default function PacketLossChart({ series = [] }) {


    if (!series || series.length === 0) {

        return <p>No packet loss data available.</p>;

    }



    const data = {


        labels: series.map(point =>

            new Date(point.t).toLocaleTimeString()

        ),



        datasets: [

            {


                label: "Packet Loss (%)",


                data: series.map(

                    point => point.loss_pct

                ),



                borderColor: "#dc2626",


                backgroundColor:
                    "rgba(220, 38, 38, 0.2)",



                borderWidth: 3,


                tension: 0.3,


                pointRadius: 4,


                pointBackgroundColor:"#dc2626"


            }

        ]

    };




    const options = {


        responsive:true,


        maintainAspectRatio:false,


        plugins:{


            legend:{


                labels:{


                    color:"#333"


                }


            }


        },


        scales:{


            x:{


                ticks:{


                    color:"#555"


                },


                grid:{


                    color:"#e5e7eb"


                }


            },



            y:{


                beginAtZero:true,


                max:100,


                ticks:{


                    color:"#555",


                    callback:(value)=>`${value}%`


                },


                grid:{


                    color:"#e5e7eb"


                }


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