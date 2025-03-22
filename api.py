import os
from datetime import date, datetime
from typing import Annotated

from fastapi import FastAPI, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pyutils.shortcuts import week_range_from_date
from rgarmin.client import GarminClient
from rgarmin.client_mock import GarminMockClient

DEBUG = os.getenv("DEBUG", False)

app = FastAPI()
garmin = GarminMockClient() if DEBUG else GarminClient()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html.jinja2")


@app.get("/connections")
async def list_connections(
    request: Request,
    hx_request: Annotated[str | None, Header()] = None,
):
    connections = garmin.get_connections()
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="connections.html.jinja2",
            context={"connections": connections},
        )
    return JSONResponse(content=jsonable_encoder(connections))


@app.get("/activities")
async def list_activities(
    request: Request,
    connections: list[str] = Query(...),
    start_date: date = Query(datetime.today().date()),
    end_date: date | None = Query(None),
    hx_request: Annotated[str | None, Header()] = None,
):
    assert len(connections) > 0, "no connections"
    assert len(connections) <= 5, "too many connections"  # testing limit to avoid over-requesting

    if not end_date:
        start_date, end_date = week_range_from_date(start_date)

    # TODO: in the tamplete, we need to group the activities by weekday
    # TODO: display the activities showing which connection did it

    connection_profiles = garmin.get_connections()
    response = {
        "start_date": start_date,
        "end_date": end_date,
        "connections": [
            {
                "display_name": connection,
                "profile": next(c for c in connection_profiles if c.display_name == connection),
                "activities": garmin.get_connection_activities_by_date(connection, start_date, end_date),
            }
            for connection in connections
        ],
    }
    if hx_request:
        return templates.TemplateResponse(
            request=request,
            name="activities.html.jinja2",
            context=response,
        )
    return JSONResponse(content=jsonable_encoder(response))
