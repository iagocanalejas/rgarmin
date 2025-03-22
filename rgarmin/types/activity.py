import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from inspect import signature
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActivityType:
    type_id: int
    type_key: str
    parent_type_id: int
    is_hidden: bool
    restricted: bool
    trimmable: bool

    @classmethod
    def from_dict(cls, data: dict) -> "ActivityType":
        valid_keys = set(signature(ActivityType).parameters.keys())
        return cls(**{k: v for k, v in data.items() if k in valid_keys})


@dataclass(frozen=True)
class ActivityListItem:
    activity_id: int
    activity_name: str
    start_time_local: datetime
    start_time_gmt: datetime
    activity_type: ActivityType
    weekday: str
    distance: float | None = None
    duration: float | None = None
    elapsed_duration: float | None = None
    moving_duration: float | None = None
    average_speed: float | None = None
    has_images: bool | None = None
    average_hr: float | None = None
    max_hr: float | None = None
    sport_type_id: int | None = None
    device_id: int | None = None
    split_summaries: list[str] | None = None
    has_splits: bool | None = None
    aerobic_training_effect: float | None = None
    anaerobic_training_effect: float | None = None
    hr_time_in_zone_1: float | None = None
    hr_time_in_zone_2: float | None = None
    hr_time_in_zone_3: float | None = None
    hr_time_in_zone_4: float | None = None
    hr_time_in_zone_5: float | None = None
    summarized_exercise_sets: list[dict[str, Any]] | None = None
    total_sets: int | None = None
    total_reps: int | None = None
    active_sets: int | None = None
    max_speed: float | None = None
    avg_stride_length: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ActivityListItem":
        data["activity_type"] = ActivityType.from_dict(data["activity_type"])
        data["start_time_local"] = datetime.fromisoformat(data["start_time_local"])
        data["start_time_gmt"] = datetime.fromisoformat(data["start_time_gmt"])
        data["weekday"] = data["start_time_local"].strftime("%A")

        valid_keys = set(signature(ActivityListItem).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})


@dataclass(frozen=True)
class Summary:
    distance: float
    duration: float
    moving_duration: float
    average_speed: float
    calories: float
    average_hr: float
    max_hr: float
    start_time_gmt: datetime
    start_time_local: datetime
    elapsed_duration: float
    bmr_calories: float
    average_temperature: float
    max_temperature: float
    min_temperature: float
    training_effect: float
    anaerobic_training_effect: float
    aerobic_training_effect_message: str
    anaerobic_training_effect_message: str
    water_estimated: float
    training_effect_label: str
    activity_training_load: float
    min_activity_lap_duration: float
    moderate_intensity_minutes: float
    vigorous_intensity_minutes: float
    max_speed: float | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    elevation_gain: float | None = None
    elevation_loss: float | None = None
    max_elevation: float | None = None
    min_elevation: float | None = None
    average_moving_speed: float | None = None
    average_run_cadence: float | None = None
    max_run_cadence: float | None = None
    average_power: float | None = None
    max_power: float | None = None
    min_power: float | None = None
    normalized_power: float | None = None
    total_work: float | None = None
    ground_contact_time: float | None = None
    stride_length: float | None = None
    vertical_oscillation: float | None = None
    vertical_ratio: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None
    max_vertical_speed: float | None = None
    steps: int | None = None
    begin_potential_stamina: float | None = None
    end_potential_stamina: float | None = None
    min_available_stamina: float | None = None
    avg_grade_adjusted_speed: float | None = None
    difference_body_battery: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Summary":
        valid_keys = set(signature(Summary).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})


@dataclass(frozen=True)
class Activity:
    activity_id: int
    activity_name: str
    activity_type: ActivityType
    summary: Summary

    @property
    def activity_start(self) -> datetime:
        local_diff = self.summary.start_time_local - self.summary.start_time_gmt
        local_offset = timezone(local_diff)
        gmt_time = datetime.fromtimestamp(self.summary.start_time_gmt.timestamp() / 1000, timezone.utc)
        return gmt_time.astimezone(local_offset)

    @classmethod
    def from_dict(cls, data: dict) -> "Activity":
        data = {k.replace("_dto", ""): v for k, v in data.items()}
        data["activity_type"] = ActivityType.from_dict(data["activity_type"])
        data["summary"] = Summary.from_dict(data["summary"])

        valid_keys = set(signature(Activity).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})
