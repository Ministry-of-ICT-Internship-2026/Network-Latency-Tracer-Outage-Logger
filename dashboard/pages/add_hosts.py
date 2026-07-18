import streamlit as st

from dashboard.components.host_manager import add_host


st.title("➕ Add Monitoring Host")


hostname = st.text_input(
    "Host name",
    placeholder="Google DNS"
)


ip_address = st.text_input(
    "IP Address",
    placeholder="8.8.8.8"
)



if st.button("Add Host"):

    if hostname and ip_address:

        success, message = add_host(
            hostname,
            ip_address
        )


        if success:

            st.cache_data.clear()

            st.success(
                message
            )


        else:

            st.error(
                message
            )


    else:

        st.warning(
            "Fill in required fields"
        )
