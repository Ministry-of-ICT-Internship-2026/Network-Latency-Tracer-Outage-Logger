import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.routes import hosts
from api.routes import analytics
from api.routes import reports


from run_monitor import start_monitor



app = FastAPI()



monitor_task = None




app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)




app.include_router(
    hosts.router,
    prefix="/api/hosts",
    tags=["Hosts"]
)



app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"]
)



app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Reports"]
)





@app.on_event("startup")
async def startup_event():

    global monitor_task


    print("Starting network monitor...")


    monitor_task = asyncio.create_task(
        start_monitor()
    )





@app.on_event("shutdown")
async def shutdown_event():

    global monitor_task


    if monitor_task:

        monitor_task.cancel()


        print(
            "Network monitor stopped"
        )





@app.get("/")
def home():

    return {
        "status": "Network API running"
    }