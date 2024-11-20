from datetime import datetime

# For compliance with python 3.9 syntax
from pydantic import BaseModel, ConfigDict
from shapely import Point, Polygon
from shapely.geometry import mapping, shape
from typing import Union, ClassVar

class Port(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders = {
                Point: lambda point: mapping(point),
                Polygon: lambda polygon: mapping(polygon),
            },
        )
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

class PostListView(Port):
    geometry_point: ClassVar[Union[Point, None]] = None
    geometry_buffer: ClassVar[Union[Polygon, None]] = None