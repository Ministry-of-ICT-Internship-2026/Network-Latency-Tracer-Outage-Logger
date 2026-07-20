from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import hosts
from api.routes import analytics
from api.routes import reports


app = FastAPI()



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


@app.get("/")
def home():

    return {
        "status": "Network API running"
    }