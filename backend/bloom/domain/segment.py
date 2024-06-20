from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel, ConfigDict
from shapely import Point,Geometry
from shapely.geometry import mapping, shape


class Segment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,
        json_encoders = {
                Geometry: lambda geometry: mapping(geometry),
            },
    )
    id: Union[int, None] = None
    excursion_id: int
    timestamp_start: Union[datetime, None] = None
    timestamp_end: Union[datetime, None] = None
    segment_duration: Union[timedelta, None] = None
    start_position: Union[Point, None] = None
    end_position: Union[Point, None] = None
    course: Union[float, None] = None
    distance: Union[float, None] = None
    average_speed: Union[float, None] = None
    speed_at_start: Union[float, None] = None
    speed_at_end: Union[float, None] = None
    heading_at_start: Union[float, None] = None
    heading_at_end: Union[float, None] = None
    type: Union[str, None] = None
    in_amp_zone: Union[bool, None] = None
    in_territorial_waters: Union[bool, None] = None
    in_costal_waters: Union[bool, None] = None
    last_vessel_segment: Union[bool, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def __hash__(self):
        return self.id
