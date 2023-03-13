from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import BaseModel, validator


class Vessel(BaseModel):
    timestamp: datetime | None
    ship_name: str | None
    IMO: str
    last_position_time: datetime | None
    latitude: float | None
    longitude: float | None
    status: str | None
    speed: float | None
    navigation_status: str | None

    def to_list(self) -> list:
        return [
            self.timestamp,
            self.ship_name,
            self.IMO,
            self.last_position_time,
            self.latitude,
            self.longitude,
        ]

    @validator("timestamp", pre=True)
    def format_timestamp(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:%M UTC").replace(
            tzinfo=timezone.utc,
        )

    @validator("last_position_time", pre=True)
    def format_last_position_time(cls, value: str) -> datetime | None:
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M UTC").replace(
                tzinfo=timezone.utc,
            )
        return None

    @validator("latitude", "longitude", pre=True)
    def format_coordinates(cls, value: str) -> float | None:
        if isinstance(value, str):
            return float(value)
        return None


class AbstractVessel(ABC):
    @abstractmethod
    def load_vessel_identifiers(self) -> list[Vessel]:
        raise NotImplementedError

    @abstractmethod
    def save_vessels(self, vessels_list: list[Vessel]) -> None:
        raise NotImplementedError
