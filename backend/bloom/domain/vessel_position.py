from datetime import datetime

from pydantic import BaseModel, ConfigDict
from shapely import Point

from typing import Union


class VesselPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Union[int, None] = None
    timestamp: datetime
    accuracy: Union[str, None] = None
    collection_type: Union[str, None] = None
    course: Union[float, None] = None
    heading: Union[float, None] = None
    position: Union[Point, None] = None
    latitude: Union[float, None] = None
    longitude: Union[float, None] = None
    maneuver: Union[str, None] = None
    navigational_status: Union[str, None] = None
    rot: Union[float, None] = None
    speed: Union[float, None] = None
    vessel_id: int
    created_at: Union[datetime, None] = None
