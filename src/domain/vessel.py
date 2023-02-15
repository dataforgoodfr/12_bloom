from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, validator


class Vessel(BaseModel):
    timestamp: Optional[datetime]
    ship_name: Optional[str]
    IMO: str
    last_position_time: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]

    def to_list(self):
        return [
            self.timestamp,
            self.ship_name,
            self.IMO,
            self.last_position_time,
            self.latitude,
            self.longitude,
        ]

    @validator("timestamp", pre=True)
    def format_timestamp(cls, value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M UTC").replace(
            tzinfo=timezone.utc
        )

    @validator("last_position_time", pre=True)
    def format_last_position_time(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M UTC").replace(
                tzinfo=timezone.utc
            )
        else:
            return None

    @validator("latitude", "longitude", pre=True)
    def format_coordinates(cls, value):
        if isinstance(value, str):
            return float(value)
        else:
            return None


class AbstractVessel(ABC):
    @abstractmethod
    def load_vessel_identifiers(self) -> List[Vessel]:
        raise NotImplementedError

    @abstractmethod
    def save_vessels(self, vessels_list: List[Vessel]) -> None:
        raise NotImplementedError
