import logging
from dataclasses import dataclass
from datetime import date
from inspect import signature

from garth import http

from pyutils.strings import camel_to_snake_dict

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PowerFormat:
    format_id: int
    format_key: str
    min_fraction: int
    max_fraction: int
    grouping_used: bool
    display_format: str | None


@dataclass(frozen=True)
class FirstDayOfWeek:
    day_id: int
    day_name: str
    sort_order: int
    is_possible_first_day: bool


@dataclass(frozen=True)
class WeatherLocation:
    use_fixed_location: bool
    latitude: float
    longitude: float
    location_name: str
    iso_country_code: str
    postal_code: str


@dataclass(frozen=True)
class UserData:
    gender: str
    weight: float
    height: float
    time_format: str
    birth_date: date
    measurement_system: str
    activity_level: str | None
    handedness: str
    power_format: PowerFormat
    heart_rate_format: PowerFormat
    first_day_of_week: FirstDayOfWeek
    vo_2_max_running: float | None
    vo_2_max_cycling: float | None
    lactate_threshold_speed: float | None
    lactate_threshold_heart_rate: float | None
    dive_number: int | None
    intensity_minutes_calc_method: str
    moderate_intensity_minutes_hr_zone: int
    vigorous_intensity_minutes_hr_zone: int
    hydration_measurement_unit: str
    hydration_containers: list[dict[str, float | None]]
    hydration_auto_goal_enabled: bool
    firstbeat_max_stress_score: float | None
    firstbeat_cycling_lt_timestamp: int | None
    firstbeat_running_lt_timestamp: int | None
    threshold_heart_rate_auto_detected: bool
    ftp_auto_detected: bool | None
    training_status_paused_date: str | None
    weather_location: WeatherLocation | None
    golf_distance_unit: str
    golf_elevation_unit: str | None
    golf_speed_unit: str | None
    external_bottom_time: float | None

    @classmethod
    def from_dict(cls, data: dict) -> "UserData":
        data["power_format"] = PowerFormat(**data["power_format"])
        data["heart_rate_format"] = PowerFormat(**data["heart_rate_format"])
        data["first_day_of_week"] = FirstDayOfWeek(**data["first_day_of_week"])
        data["weather_location"] = WeatherLocation(**data["weather_location"])
        data["birth_date"] = date.fromisoformat(data["birth_date"])

        valid_keys = set(signature(UserData).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})


@dataclass(frozen=True)
class UserSleep:
    sleep_time: int
    default_sleep_time: bool
    wake_time: int
    default_wake_time: bool


@dataclass(frozen=True)
class UserSettings:
    id: int
    user_data: UserData
    user_sleep: UserSleep
    connect_date: str | None
    source_type: str | None

    @classmethod
    def get(cls, /, client: http.Client | None = None):
        client = client or http.client
        settings = client.connectapi("/userprofile-service/userprofile/user-settings")
        assert isinstance(settings, dict)
        return cls.from_dict(camel_to_snake_dict(settings))

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        data["user_data"] = UserData.from_dict(data["user_data"])
        data["user_sleep"] = UserSleep(**data["user_sleep"])
        return cls(**data)
