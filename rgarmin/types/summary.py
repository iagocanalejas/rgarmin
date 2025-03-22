import logging
from dataclasses import dataclass
from inspect import signature

logger = logging.getLogger(__name__)


@dataclass
class DailySummary:
    user_profile_id: int
    total_kilocalories: float
    active_kilocalories: float
    bmr_kilocalories: float
    wellness_kilocalories: float
    burned_kilocalories: float | None
    consumed_kilocalories: float | None
    remaining_kilocalories: float | None
    total_steps: int
    net_calorie_goal: float | None
    total_distance_meters: int
    wellness_distance_meters: int
    wellness_active_kilocalories: float
    net_remaining_kilocalories: float
    user_daily_summary_id: int
    calendar_date: str
    uuid: str
    daily_step_goal: int
    wellness_start_time_gmt: str
    wellness_start_time_local: str
    wellness_end_time_gmt: str
    wellness_end_time_local: str
    duration_in_milliseconds: int
    wellness_description: str | None
    highly_active_seconds: int
    active_seconds: int
    sedentary_seconds: int
    sleeping_seconds: int
    includes_wellness_data: bool
    includes_activity_data: bool
    includes_calorie_consumed_data: bool
    privacy_protected: bool
    moderate_intensity_minutes: int
    vigorous_intensity_minutes: int
    floors_ascended_in_meters: float
    floors_descended_in_meters: float
    floors_ascended: float
    floors_descended: float
    intensity_minutes_goal: int
    user_floors_ascended_goal: int
    min_heart_rate: int
    max_heart_rate: int
    resting_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int
    source: str
    average_stress_level: int
    max_stress_level: int
    stress_duration: int
    rest_stress_duration: int
    activity_stress_duration: int
    uncategorized_stress_duration: int | None
    total_stress_duration: int
    low_stress_duration: int
    medium_stress_duration: int
    high_stress_duration: int | None
    stress_percentage: float
    rest_stress_percentage: float
    activity_stress_percentage: float
    uncategorized_stress_percentage: float
    low_stress_percentage: float
    medium_stress_percentage: float
    high_stress_percentage: float
    stress_qualifier: str
    measurable_awake_duration: int
    measurable_asleep_duration: int
    last_sync_timestamp_gmt: str
    min_avg_heart_rate: int
    max_avg_heart_rate: int
    body_battery_charged_value: int
    body_battery_drained_value: int
    body_battery_highest_value: int
    body_battery_lowest_value: int
    body_battery_most_recent_value: int
    body_battery_during_sleep: int
    body_battery_at_wake_time: int
    body_battery_version: float
    abnormal_heart_rate_alerts_count: int | None
    average_spo_2: float | None
    lowest_spo_2: float | None
    latest_spo_2: float | None
    latest_spo_2_reading_time_gmt: str | None
    latest_spo_2_reading_time_local: str | None
    average_monitoring_environment_altitude: float
    resting_calories_from_activity: int | None
    highest_respiration_value: float
    lowest_respiration_value: float
    latest_respiration_value: float
    latest_respiration_time_gmt: str
    respiration_algorithm_version: int
    avg_waking_respiration_value: float

    @classmethod
    def from_dict(cls, data: dict) -> "DailySummary":
        valid_keys = set(signature(DailySummary).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})
