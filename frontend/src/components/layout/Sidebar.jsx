import { NavLink } from "react-router-dom";

import "../../styles/sidebar.css";


export default function Sidebar(){

    return (

        <aside className="sidebar">


            <h2 className="sidebar-logo">
                NetMonitor
            </h2>



            <nav className="sidebar-nav">


                <NavLink
                    to="/"
                    className="sidebar-link"
                >
                    Dashboard
                </NavLink>



                <NavLink
                    to="/fleet"
                    className="sidebar-link"
                >
                    Hosts
                </NavLink>



                <NavLink
                    to="/reports"
                    className="sidebar-link"
                >
                    Reports
                </NavLink>



                <NavLink
                    to="/settings"
                    className="sidebar-link"
                >
                    Settings
                </NavLink>


            </nav>


        </aside>

    );

}