import SettingsCard from "../components/settings/SettingsCard";

import ConfigForm from "../components/settings/ConfigForm";
import SystemInfo from "../components/settings/SystemInfo";

import "../styles/settings.css";


export default function Settings(){


    return (

        <div className="settings-page">


            <h1>
                Settings
            </h1>


            <p>
                Configure network monitoring behaviour.
            </p>





            <SettingsCard
                title="Monitoring Configuration"
            >

                <ConfigForm />

            </SettingsCard>






            <SettingsCard
                title="System Information"
            >

                <SystemInfo />

            </SettingsCard>





            <SettingsCard
                title="Database"
            >

                <p>
                    <strong>Status:</strong>
                    {" "}
                    🟢 Connected
                </p>


                <p>
                    <strong>Type:</strong>
                    {" "}
                    SQLite
                </p>


                <p>
                    <strong>Location:</strong>
                    {" "}
                    database/latency.db
                </p>


            </SettingsCard>




        </div>

    );

}