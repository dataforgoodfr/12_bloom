from datetime import datetime, timedelta

from pydantic import BaseModel

from typing import Union


class Excursion(BaseModel):
    id: int | None = None
    vessel_id: int
    departure_port_id: Union[int, None] = None
    departure_at: Union[datetime, None] = None
    departure_position_id: int
    arrival_port_id: Union[int, None] = None
    arrival_at: Union[datetime, None] = None
    arrival_position_id: int
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
