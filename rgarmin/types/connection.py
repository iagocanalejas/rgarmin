import logging
from dataclasses import dataclass
from inspect import signature

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Connection:
    user_id: int
    display_name: str
    full_name: str
    location: str
    user_level: int
    profile_image_url_small: str
    profile_image_url_medium: str
    profile_image_url_large: str

    @classmethod
    def from_dict(cls, data: dict) -> "Connection":
        valid_keys = set(signature(Connection).parameters.keys())
        logger.debug(f"ignoring keys: {set(data.keys()) - valid_keys}")
        return cls(**{k: v for k, v in data.items() if k in valid_keys})
