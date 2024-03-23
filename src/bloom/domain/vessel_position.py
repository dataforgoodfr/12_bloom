from datetime import datetime

from pydantic import BaseModel
from shapely import Point

from typing import Union


class VesselPosition(BaseModel):
    id: int | None = None
    timestamp: datetime
    accuracy: Union[str, None] = None
    collection_type: Union[str, None] = None
    course: Union[float, None] = None
    heading: Union[float, None] = None
    position: Union[Point, None] = None
    latitude: float | None
    longitude: float | None
    maneuver: str | None
    navigational_status: str | None
    rot: float | None
    speed: float | None
    vessel_id: int
    created_at: Union[datetime, None] = None
