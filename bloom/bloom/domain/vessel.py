from datetime import datetime, timezone

from pydantic import BaseModel, validator
from shapely import Point

from typing import Union


class Vessel(BaseModel):
    vessel_id: int
    ship_name: Union[str, None]
    IMO: Union[str, None]
    mmsi: Union[int, None]

    def get_mmsi(self) -> int:
        return self.mmsi


class VesselPositionMarineTraffic(BaseModel):
    timestamp: Union[datetime, None]
    ship_name: Union[str, None]
    current_port: Union[str, None]
    IMO: Union[str, None]
    vessel_id: int
    mmsi: Union[str, None]
    last_position_time: Union[datetime, None]
    ship_name: Union[str, None]
    IMO: str
    mmsi: Union[str, None]
    fishing: Union[ bool, None]
    at_port: Union[ bool, None]
    position: Union[Point, None]
    status: Union[str, None]
    speed: Union[float, None]
    navigation_status: Union[str, None]

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
    def format_last_position_time(cls, value: str) -> Union [ datetime, None ]:
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M UTC").replace(
                tzinfo=timezone.utc,
            )
        return None
