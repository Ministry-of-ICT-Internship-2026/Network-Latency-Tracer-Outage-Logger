import { Outlet } from "react-router-dom";

import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

import "../../styles/layout.css";


export default function DashboardLayout(){


    return (

        <div className="dashboard-layout">


            <Sidebar />


            <div className="dashboard-main">


                <Navbar />


                <main className="page-content">

                    <Outlet />

                </main>


            </div>


        </div>

    );

}