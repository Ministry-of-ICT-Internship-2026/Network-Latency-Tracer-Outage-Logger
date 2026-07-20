from fastapi import APIRouter, HTTPException

from monitoring.database import DatabaseManager


router = APIRouter()



# ---------------------------------------
# Get all monitored hosts
# ---------------------------------------

@router.get("/")
def get_hosts():

    db = DatabaseManager()

    try:

        hosts = db.get_hosts()


        return [

            {
                "id": host["id"],
                "hostname": host["hostname"],
                "ip_address": host["ip_address"],
                "enabled": bool(host["enabled"]),
                "created_at": host["created_at"]
            }

            for host in hosts

        ]


    finally:

        db.close()





# ---------------------------------------
# Add a new host
# ---------------------------------------

@router.post("/")
def create_host(host: dict):

    db = DatabaseManager()

    try:

        db.add_host(
            host["hostname"],
            host["ip_address"]
        )


        return {

            "message": "Host added successfully"

        }


    except Exception as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)

        )


    finally:

        db.close()





# ---------------------------------------
# Delete host
# ---------------------------------------

@router.delete("/{host_id}")
def remove_host(host_id: int):

    db = DatabaseManager()

    try:

        db.delete_host(
            host_id
        )


        return {

            "message": "Host deleted"

        }


    finally:

        db.close()





# ---------------------------------------
# Toggle host enabled/disabled
# ---------------------------------------

@router.patch("/{host_id}/toggle")
def toggle_host(host_id: int):

    db = DatabaseManager()

    try:

        cursor = db.connection.cursor()


        cursor.execute(
            """
            SELECT enabled
            FROM hosts
            WHERE id=?
            """,
            (host_id,)
        )


        host = cursor.fetchone()



        if not host:

            raise HTTPException(

                status_code=404,

                detail="Host not found"

            )



        new_status = 0 if host["enabled"] else 1



        cursor.execute(
            """
            UPDATE hosts
            SET enabled=?
            WHERE id=?
            """,
            (
                new_status,
                host_id
            )
        )


        db.connection.commit()



        return {

            "message": "Host status updated",

            "enabled": bool(new_status)

        }



    finally:

        db.close()