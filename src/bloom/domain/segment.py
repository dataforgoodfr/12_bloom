from datetime import datetime, timedelta

from pydantic import BaseModel
from shapely import Point, Polygon

from typing import Union


class Excursion(BaseModel):
    id: int | None = None
    excursion_id: int
    timestamp_start: Union[datetime, None] = None
    timestamp_end: Union[datetime, None] = None
    segment_duration: Union[timedelta, None] = None
    start_position_id: Union[int, None] = None
    end_position_id: Union[int, None] = None
    heading: Union[float | None] = None
    distance: Union[float | None] = None
    average_speed: Union[float | None] = None
    type: Union[str | None] = None
    in_amp_zone: Union[bool | None] = None
    in_territorial_waters: Union[bool | None] = None
    in_costal_waters: Union[bool | None] = None
    last_vessel_segment: Union[bool | None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
