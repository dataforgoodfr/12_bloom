from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import BaseModel, validator
from shapely import Point


class VesselPositionMarineTraffic(BaseModel):
    timestamp: datetime | None
    ship_name: str | None
    IMO: str
    mmsi: str
    last_position_time: datetime | None
    fishing: bool
    at_port: bool
    position: Point | None
    status: str | None
    speed: float | None
    navigation_status: str | None

    def to_list(self) -> list:
        return [
            self.timestamp,
            self.ship_name,
            self.IMO,
            self.last_position_time,
            self.position.__str__(),
            self.status,
            self.speed,
            self.navigation_status,
        ]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Point: lambda v: (v.x, v.y),
        }

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


class AbstractVessel(ABC):
    @abstractmethod
    def load_vessel_identifiers(self) -> list[VesselPositionMarineTraffic]:
        raise NotImplementedError

    @abstractmethod
    def save_vessels(self, vessels_list: list[VesselPositionMarineTraffic]) -> None:
        raise NotImplementedError
