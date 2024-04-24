from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel, ConfigDict
from shapely import Point


class Excursion(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Union[int, None] = None
    vessel_id: int
    departure_port_id: Union[int, None] = None
    departure_at: Union[datetime, None] = None
    departure_position: Union[Point, None] = None
    arrival_port_id: Union[int, None] = None
    arrival_at: Union[datetime, None] = None
    arrival_position: Union[Point, None] = None
    excursion_duration: Union[timedelta, None] = None
    total_time_at_sea: Union[timedelta, None] = None
    total_time_in_amp: Union[timedelta, None] = None
    total_time_in_territorial_waters: Union[timedelta, None] = None
    total_time_in_costal_waters: Union[timedelta, None] = None
    total_time_fishing: Union[timedelta, None] = None
    total_time_fishing_in_amp: Union[timedelta, None] = None
    total_time_fishing_in_territorial_waters: Union[timedelta, None] = None
    total_time_fishing_in_costal_waters: Union[timedelta, None] = None
    total_time_extincting_amp: Union[timedelta, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
