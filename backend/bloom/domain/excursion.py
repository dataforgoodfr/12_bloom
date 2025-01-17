from datetime import datetime, timedelta
from typing import Union

from pydantic import BaseModel, ConfigDict
from shapely import Geometry, Point, MultiPolygon,Polygon
from shapely.geometry import mapping, shape


class Excursion(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,
        json_encoders = {
                #Point: lambda point: mapping(point) if point != None else None,
                Geometry: lambda p: mapping(p),
            },)
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
    total_time_in_zones_with_no_fishing_rights: Union[timedelta, None] = None
    total_time_fishing: Union[timedelta, None] = None
    total_time_fishing_in_amp: Union[timedelta, None] = None
    total_time_fishing_in_territorial_waters: Union[timedelta, None] = None
    total_time_fishing_in_zones_with_no_fishing_rights: Union[timedelta, None] = None
    total_time_default_ais: Union[timedelta, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
