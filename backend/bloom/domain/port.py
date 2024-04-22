from datetime import datetime

# For compliance with python 3.9 syntax
from pydantic import BaseModel, ConfigDict
from shapely import Point, Polygon

from typing import Union


class Port(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Union[int, None] = None
    name: str
    locode: str
    url: Union[str, None] = None
    country_iso3: Union[str, None] = None
    latitude: Union[float, None] = None
    longitude: Union[float, None] = None
    geometry_point: Union[Point, None] = None
    geometry_buffer: Union[Polygon, None] = None
    has_excursion: bool = False
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
