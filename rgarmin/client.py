import logging
from datetime import date, datetime
from enum import StrEnum
from getpass import getpass

import garth as g
from garth.exc import GarthHTTPError

from pyutils.dicts import camel_to_snake_dict
from rgarmin.types import Activity, ActivityListItem, ActivityType, Connection, DailySummary, UserProfile, UserSettings

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 20  # same limit the real Garmin Connect uses


class GarminClient:
    garth: g.Client
    profile: UserProfile
    settings: UserSettings
    _activity_types: list[ActivityType] = []

    @classmethod
    def to_garmin_date(cls, dt: date) -> str:
        return dt.strftime("%Y-%m-%d")

    @property
    def display_name(self) -> str:
        return self.profile.display_name

    @property
    def full_name(self) -> str:
        return self.profile.full_name

    @property
    def unit_system(self) -> str:
        return self.settings.user_data.measurement_system

    @property
    def activity_types(self) -> list[ActivityType]:
        if not self._activity_types:
            response = self.garth.connectapi(self.ConnectURL.ACTIVITY_TYPES)
            assert response is not None, "failed to get activity types"
            assert all(isinstance(a, dict) for a in response), "invalid activity type data"
            self._activity_types = [
                ActivityType.from_dict(a) for a in [camel_to_snake_dict(r) for r in response if isinstance(r, dict)]
            ]
        return self._activity_types

    def __init__(self, is_cn=False, tokenstore=".garminconnect"):
        self.garth = g.Client(
            domain="garmin.cn" if is_cn else "garmin.com",
            pool_connections=20,
            pool_maxsize=20,
        )

        try:
            self.garth.load(tokenstore)
        except (FileNotFoundError, GarthHTTPError):
            logger.error(f"token store not found: {tokenstore}")

            email = input("Login e-mail: ")
            password = getpass("Enter password: ")
            self.garth.login(email, password)

            # save Oauth1 and Oauth2 token files to directory for next login
            self.garth.dump(tokenstore)

        self.profile = UserProfile.from_dict(camel_to_snake_dict(self.garth.profile))
        self.settings = UserSettings.get(self.garth)
        logger.info(f"logged in as {self.display_name}")

    def get_user_summary(self, cdate: str, display_name: str | None = None) -> DailySummary:
        logger.debug("requesting user summary")
        response = self.garth.connectapi(
            f"{self.ConnectURL.DAILY_SUMMARY}/{display_name or self.display_name}",
            params={"calendarDate": str(cdate)},
        )
        assert response is not None, "failed to get user summary"
        assert not response["privacyProtected"], "user summary is private"
        return DailySummary.from_dict(camel_to_snake_dict(response))

    def get_activities(self, start: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> list[ActivityListItem]:
        logger.debug("requesting activities")
        response = self.garth.connectapi(
            self.ConnectURL.ACTIVITIES,
            params={"start": start, "limit": limit},
        )
        assert response is not None, "failed to get activities"
        assert all(isinstance(a, dict) for a in response), "invalid activity data"
        return [ActivityListItem.from_dict(camel_to_snake_dict(a)) for a in response if isinstance(a, dict)]

    def get_activity(self, activity_id: str) -> Activity:
        logger.debug(f"Requesting activity summary data for activity id {activity_id}")
        response = self.garth.connectapi(f"{self.ConnectURL.ACTIVITY}/{activity_id}")
        assert response is not None, "failed to get activity"
        return Activity.from_dict(camel_to_snake_dict(response))

    def get_activities_by_date(
        self,
        start_date: date,
        end_date: date,
        activity_type: str | None = None,
    ) -> list[ActivityListItem]:
        """
        Fetch available activities between specific dates
        :param start_date: Datetime to be formated as YYYY-MM-DD
        :param enddate: (Optional) Datetime to be formated as YYYY-MM-DD
        :param activity_type: (Optional) Type of activity you are searching
        """
        logger.debug(f"requesting activities between {start_date} and {end_date}")

        activities = []
        start = 0

        # mimicking the behavior of the web interface that fetches 20 activities at a time and loads more on scroll
        params = {
            "startDate": self.to_garmin_date(start_date),
            "start": str(start),
            "limit": str(DEFAULT_PAGE_SIZE),
        }
        if end_date:
            params["endDate"] = self.to_garmin_date(end_date)
        if activity_type:
            params["activityType"] = str(activity_type)

        while True:
            logger.debug(f"requesting activities {start} to {start + DEFAULT_PAGE_SIZE}")
            params["start"] = str(start)
            response = self.garth.connectapi(self.ConnectURL.ACTIVITIES, params=params)
            if not response:
                break
            activities.extend(
                [ActivityListItem.from_dict(camel_to_snake_dict(a)) for a in response if isinstance(a, dict)]
            )
            start = start + DEFAULT_PAGE_SIZE

        return activities

    def get_connections(self, start: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> list[Connection]:
        logger.debug("requesting connections")
        response = self.garth.connectapi(
            self.ConnectURL.CONNECTIONS,
            params={"start": start, "limit": limit},
        )
        assert response is not None, "failed to get connections"
        return [Connection.from_dict(a) for a in camel_to_snake_dict(response)["user_connections"]]

    def get_connection(self, display_name: str) -> UserProfile:
        logger.debug(f"requesting connection for {display_name}")
        response = self.garth.connectapi(f"{self.ConnectURL.CONNECTION}/{display_name}")
        assert response is not None, "failed to get connection"
        return UserProfile.from_dict(camel_to_snake_dict(response))

    def get_connection_activities(
        self,
        display_name: str,
        start: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> list[ActivityListItem]:
        logger.debug(f"requesting activities for connection {display_name}")
        response = self.garth.connectapi(
            f"{self.ConnectURL.ACTIVITIES_BASEURL}/{display_name}",
            params={"start": start, "limit": limit},
        )
        assert response is not None, "failed to get connection activities"
        return [ActivityListItem.from_dict(a) for a in camel_to_snake_dict(response)["activity_list"]]

    def get_connection_activities_by_date(
        self,
        display_name: str,
        start_date: date,
        end_date: date,
    ) -> list[ActivityListItem]:
        """
        Fetch available activities between specific dates
        :param display_name: Display name of the user
        :param start_date: Datetime to be formated as YYYY-MM-DD
        :param end_date: Datetime to be formated as YYYY-MM-DD
        """
        logger.debug(f"requesting activities between {start_date} and {end_date}")

        activities = []
        start = 0

        # mimicking the behavior of the web interface that fetches 20 activities at a time and loads more on scroll
        while True:
            logger.debug(f"requesting activities {start} to {start + DEFAULT_PAGE_SIZE}")
            response = self.garth.connectapi(
                f"{self.ConnectURL.ACTIVITIES_BASEURL}/{display_name}",
                params={"start": start, "limit": DEFAULT_PAGE_SIZE},
            )
            assert response is not None, "failed to get connection activities"

            activity_list = response.get("activityList", [])
            if not activity_list:
                return activities

            for a in activity_list:
                if datetime.fromisoformat(a["startTimeLocal"]).date() < start_date:
                    return activities
                if datetime.fromisoformat(a["startTimeLocal"]).date() <= end_date:
                    activities.append(ActivityListItem.from_dict(camel_to_snake_dict(a)))

            start = start + DEFAULT_PAGE_SIZE

    def request_reload(self, cdate: str):
        """
        Request reload of data for a specific date.
        This is necessary because Garmin offloads older data.
        """
        logger.debug(f"requesting reload of data for {cdate}.")
        url = f"{self.ConnectURL.REQUEST_RELOAD}/{cdate}"
        return self.garth.post("connectapi", url, api=True)

    class ConnectURL(StrEnum):
        ACTIVITY_TYPES = "/activity-service/activity/activityTypes"
        ACTIVITIES_BASEURL = "/activitylist-service/activities"
        ACTIVITIES = "/activitylist-service/activities/search/activities"
        ACTIVITY = "/activity-service/activity"
        ACTIVITY_FOR_DATE = "/mobile-gateway/heartRate/forDate"
        CONNECTIONS_BASEURL = "/connection-service/connection/"
        CONNECTIONS = "connection-service/connection/connections"
        CONNECTION = "/userprofile-service/socialProfile"
        REQUEST_RELOAD = "/wellness-service/wellness/epoch/request"

        DEVICES = "/device-service/deviceregistration/devices"
        DEVICE = "/device-service/deviceservice"
        PRIMARY_DEVICE = "/web-gateway/device-info/primary-training-device"
        SOLAR = "/web-gateway/solar"
        WEIGHT = "/weight-service"
        DAILY_SUMMARY = "/usersummary-service/usersummary/daily"
        METRICS = "/metrics-service/metrics/maxmet/daily"
        DAILY_HYDRATION = "/usersummary-service/usersummary/hydration/daily"
        SET_HYDRATION = "usersummary-service/usersummary/hydration/log"
        DAILY_STATS_STEPS = "/usersummary-service/stats/steps/daily"
        PERSONAL_RECORD = "/personalrecord-service/personalrecord/prs"
        EARNED_BADGES = "/badge-service/badge/earned"
        ADHOC_CHALLENGES = "/adhocchallenge-service/adHocChallenge/historical"
        ADHOC_CHALLENGE = "/adhocchallenge-service/adHocChallenge/"
        BADGE_CHALLENGES = "/badgechallenge-service/badgeChallenge/completed"
        AVAILABLE_BADGE_CHALLENGES = "/badgechallenge-service/badgeChallenge/available"
        NON_COMPLETED_BADGE_CHALLENGES = "/badgechallenge-service/badgeChallenge/non-completed"
        INPROGRESS_VIRTUAL_CHALLENGES = "/badgechallenge-service/virtualChallenge/inProgress"
        DAILY_SLEEP = "/wellness-service/wellness/dailySleepData"
        DAILY_STRESS = "/wellness-service/wellness/dailyStress"
        HILL_SCORE = "/metrics-service/metrics/hillscore"
        DAILY_BODY_BATTERY = "/wellness-service/wellness/bodyBattery/reports/daily"
        BODY_BATTERY_EVENTS = "/wellness-service/wellness/bodyBattery/events"
        BLOOD_PRESSURE_ENDPOINT = "/bloodpressure-service/bloodpressure/range"
        SET_BLOOD_PRESSURE_ENDPOINT = "/bloodpressure-service/bloodpressure"
        ENDURANCE_SCORE = "/metrics-service/metrics/endurancescore"
        MENSTRUAL_CALENDAR = "/periodichealth-service/menstrualcycle/calendar"
        MENSTRUAL_DAYVIEW = "/periodichealth-service/menstrualcycle/dayview"
        PREGNANCY_SNAPSHOT = "periodichealth-service/menstrualcycle/pregnancysnapshot"
        GOALS = "/goal-service/goal/goals"
        RHR = "/userstats-service/wellness/daily"
        HRV = "/hrv-service/hrv"
        TRAINING_READINESS = "/metrics-service/metrics/trainingreadiness"
        RACE_PREDICTOR = "/metrics-service/metrics/racepredictions"
        TRAINING_STATUS = "/metrics-service/metrics/trainingstatus/aggregated"
        USER_SUMMARY_CHART = "/wellness-service/wellness/dailySummaryChart"
        FLOORS_CHART_DAILY = "/wellness-service/wellness/floorsChartData/daily"
        HEARTRATES_DAILY = "/wellness-service/wellness/dailyHeartRate"
        DAILY_RESPIRATION = "/wellness-service/wellness/daily/respiration"
        DAILY_SPO2 = "/wellness-service/wellness/daily/spo2"
        DAILY_INTENSITY_MINUTES = "/wellness-service/wellness/daily/im"
        ALL_DAY_STRESS = "/wellness-service/wellness/dailyStress"
        DAILY_EVENTS = "/wellness-service/wellness/dailyEvents"
        FITNESSSTATS = "/fitnessstats-service/activity"
        FITNESSAGE = "/fitnessage-service/fitnessage"
        FIT_DOWNLOAD = "/download-service/files/activity"
        TCX_DOWNLOAD = "/download-service/export/tcx/activity"
        GPX_DOWNLOAD = "/download-service/export/gpx/activity"
        KML_DOWNLOAD = "/download-service/export/kml/activity"
        CSV_DOWNLOAD = "/download-service/export/csv/activity"
        UPLOAD = "/upload-service/upload"
        GEAR = "/gear-service/gear/filterGear"
        GEAR_BASEURL = "/gear-service/gear/"
        WORKOUTS = "/workout-service"
        DELETE_ACTIVITY = "/activity-service/activity"
        GRAPHQL_ENDPOINT = "graphql-gateway/graphql"
