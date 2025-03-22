import logging
from dataclasses import dataclass
from inspect import signature

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UserProfile:
    id: int
    profile_id: int
    garmin_guid: str
    display_name: str
    full_name: str
    user_name: str
    profile_visibility: str
    user_roles: list[str]
    user_level: int

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        valid_keys = set(signature(UserProfile).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})
