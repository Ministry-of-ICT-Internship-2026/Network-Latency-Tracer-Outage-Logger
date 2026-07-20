export default function SettingsCard({
    title,
    children
}) {


    return (

        <div className="settings-card">


            <h3>
                {title}
            </h3>


            {children}


        </div>

    );

}