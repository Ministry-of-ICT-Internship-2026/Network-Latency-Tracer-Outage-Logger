import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";


import Dashboard from "./pages/Dashboard";
import Fleet from "./pages/Fleet";
import HostDetails from "./pages/HostDetails";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

import DashboardLayout from "./components/layout/DashboardLayout";



function App() {


    return (

        <BrowserRouter>


            <Routes>


                <Route
                    element={
                        <DashboardLayout />
                    }
                >


                    <Route
                        path="/"
                        element={
                            <Dashboard />
                        }
                    />


                    <Route
                        path="/fleet"
                        element={
                            <Fleet />
                        }
                    />


                    <Route
                        path="/hosts/:host"
                        element={
                            <HostDetails />
                        }
                    />


                    <Route
                        path="/reports"
                        element={
                            <Reports />
                        }
                    />


                    <Route
                        path="/settings"
                        element={
                            <Settings />
                        }
                    />


                </Route>


            </Routes>


        </BrowserRouter>

    );

}


export default App;