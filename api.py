import logging
import os
from datetime import date, datetime, timedelta

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pyutils.shortcuts import week_range_from_date, weeks_between
from rgarmin import filters
from rgarmin.client import GarminClient
from rgarmin.services import activities

DEBUG = os.getenv("DEBUG", False)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.filters["translate"] = filters.translate
templates.env.filters["format_duration"] = filters.format_duration
templates.env.filters["format_datetime"] = filters.format_datetime
templates.env.filters["format_time"] = filters.format_time

garmin = GarminClient()


@app.get("/")
async def index(_: Request):
    return RedirectResponse(url="/connections")


@app.get("/connections")
async def list_connections(request: Request, partial: bool = Query(False, alias="p")):
    connections = garmin.get_connections()
    if "text/html" in request.headers["accept"]:
        is_htmx = request.headers.get("HX-Request", False)
        return templates.TemplateResponse(
            request=request,
            name="connections.html.jinja2" if partial and is_htmx else "_base.html.jinja2",
            context={"connections": connections, "page": "connections.html.jinja2"},
        )
    return JSONResponse(content=jsonable_encoder(connections))


@app.get("/activities")
async def list_activities(
    request: Request,
    connections: list[str] = Query(...),
    start_date: date = Query(datetime.today().date()),
    end_date: date | None = Query(None),
    partial: bool = Query(False, alias="p"),
):
    if not end_date:
        start_date, end_date = week_range_from_date(start_date)

    if not connections or len(connections) == 0:
        raise HTTPException(status_code=400, detail="At least one connection is required.")
    if len(connections) > 10:
        raise HTTPException(status_code=400, detail="Too many connections. Maximum allowed: 10.")
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be greater than start date.")
    if weeks_between(start_date, end_date) > timedelta(weeks=2):
        raise HTTPException(status_code=400, detail="Maximum allowed date range is 2 weeks.")

    if "text/html" in request.headers["accept"]:
        is_htmx = request.headers.get("HX-Request", False)
        context = activities.get_html_activities(garmin, connections, start_date, end_date)
        context["page"] = "activities.html.jinja2"
        return templates.TemplateResponse(
            request=request,
            name="activities.html.jinja2" if partial and is_htmx else "_base.html.jinja2",
            context=context,
        )
    response = activities.get_json_activities(garmin, connections, start_date, end_date)
    return JSONResponse(content=jsonable_encoder(response))
