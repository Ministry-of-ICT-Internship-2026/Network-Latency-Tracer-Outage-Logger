import streamlit as st

from server.database import DatabaseManager



@st.cache_resource
def get_database():

    return DatabaseManager()



def add_host(
    hostname,
    ip_address

):

    try:
        db = get_database()

        db.add_host(
            hostname,
            ip_address
        )

        return True, "Host added successfully"

    except Exception as e:

        return False, str(e)

    db = get_database()

    db.add_host(
        hostname,
        ip_address
    )



def get_hosts():

    db = get_database()

    return db.get_hosts()



def delete_host(host_id):

    db = get_database()

    db.delete_host(
        host_id
    )