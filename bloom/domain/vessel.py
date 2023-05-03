from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import BaseModel, validator
from shapely import Point


class Vessel(BaseModel):
    vessel_id: int
    ship_name: str | None
    IMO: str | None
    mmsi: str | None


class VesselPositionMarineTraffic(BaseModel):
    timestamp: datetime | None
    ship_name: str | None
    current_port: str | None
    IMO: str | None
    vessel_id: int
    mmsi: str | None
    last_position_time: datetime | None
    at_port: bool | None
    position: Point | None
    status: str | None
    speed: float | None
    navigation_status: str | None
    fishing: bool | None

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
    def load_vessel_identifiers(self) -> list[Vessel]:
        raise NotImplementedError

    @abstractmethod
    def save_vessels_positions(
        self,
        vessels_positions_list: list[VesselPositionMarineTraffic],
    ) -> None:
        raise NotImplementedError
