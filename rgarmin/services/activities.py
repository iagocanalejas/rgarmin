import logging
from datetime import date, timedelta
from typing import Any

from garth.exc import GarthHTTPError

from pyutils.shortcuts import date_range
from rgarmin.client import GarminClient

logger = logging.getLogger(__name__)


def get_json_activities(garmin: GarminClient, connections: list[str], start_date: date, end_date: date) -> dict:
    profiles = garmin.get_connections()
    result: dict[str, Any] = {
        "pagination": _get_week_pagination(connections, start_date, end_date),
        "connection_activities": [
            {
                "display_name": garmin.profile.display_name,
                "profile": garmin.profile,
                "activities": garmin.get_activities_by_date(start_date, end_date),
            }
        ],
        "errors": {},
    }

    for connection in connections:
        try:
            result["connection_activities"].append(
                {
                    "display_name": connection,
                    "profile": next(c for c in profiles if c.display_name == connection),
                    "activities": garmin.get_connection_activities_by_date(connection, start_date, end_date),
                }
            )
        except GarthHTTPError as e:
            logger.error(f"Error fetching activities for {connection}: {e}")
            result["errors"][connection] = "_error_fetching_activities"

    return result


def _process_similar_activities(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for activity1 in activities:
        for activity2 in activities:
            if activity1["profile"].display_name == activity2["profile"].display_name:
                # activities from the same profile can't be similar
                continue
            if activity2["details"].activity_id in activity1["details"].similar_activities:
                # we add activities both ways so we can reach this point and skip a lot of activities
                continue

            if activity1["details"] == activity2["details"]:
                activity1["details"].similar_activities.append(activity2["details"].activity_id)
                activity2["details"].similar_activities.append(activity1["details"].activity_id)
    return activities


def get_html_activities(garmin: GarminClient, connections: list[str], start_date: date, end_date: date) -> dict:
    profiles = garmin.get_connections()
    results = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}
    errors = {}

    for activity in garmin.get_activities_by_date(start_date, end_date):
        results[activity.weekday].append({"profile": garmin.profile, "details": activity})

    for connection in connections:
        try:
            profile = next(c for c in profiles if c.display_name == connection)
            for activity in garmin.get_connection_activities_by_date(connection, start_date, end_date):
                results[activity.weekday].append({"profile": profile, "details": activity})
        except GarthHTTPError as e:
            logger.error(f"Error fetching activities for {connection}: {e}")
            errors[connection] = "_error_fetching_activities"

    for key, value in results.items():
        results[key] = _process_similar_activities(value)
        results[key].sort(key=lambda x: x["details"].start_time_local)

    return {
        "daily_activities": results,
        "days": [d.strftime("%d-%m-%Y") for d in date_range(start_date, end_date)],
        "pagination": _get_week_pagination(connections, start_date, end_date),
        "errors": errors,
    }


def _get_week_pagination(connections: list[str], start_date: date, end_date: date) -> dict:
    conn_url = f"connections={'&connections='.join(connections)}"
    next_url = (
        "/activities?"
        + f"{conn_url}&start_date={start_date + timedelta(weeks=1)}&end_date={end_date + timedelta(weeks=1)}"
        + "&p=True"
    )
    prev_url = (
        "/activities?"
        + f"{conn_url}&start_date={start_date - timedelta(weeks=1)}&end_date={end_date - timedelta(weeks=1)}"
        + "&p=True"
    )
    return {
        "start_date": start_date.strftime("%d-%m-%Y"),
        "end_date": end_date.strftime("%d-%m-%Y"),
        "next_url": next_url,
        "prev_url": prev_url,
    }
