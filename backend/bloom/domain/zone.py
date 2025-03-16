from datetime import datetime
from typing import Union, ClassVar

from pydantic import BaseModel, ConfigDict
from shapely import Geometry, Point, MultiPolygon,Polygon
from shapely.geometry import mapping, shape

class Zone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,
        json_encoders = {
                #Point: lambda point: mapping(point) if point != None else None,
                Geometry: lambda p: mapping(p),
            },)
    id: Union[int, None] = None
    key: Union[str, None] = None
    category: str
    sub_category: Union[str, None] = None
    name: str
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    geometry: Union[Geometry, None] = None
    centroid: Union[Point, None] = None
    json_data: Union[dict, None] = None
    enable: Union[bool, None] = None
    scd_start: Union[datetime, None] = None
    scd_end: Union[datetime, None] = None
    scd_active: Union[bool, None] = None

class ZoneSummary(BaseModel):
    id: Union[int, None] = None
    key: Union[str, None] = None
    category: str
    sub_category: Union[str, None] = None
    name: str
    created_at: Union[datetime, None] = None
    enable: Union[bool, None] = None
    scd_start: Union[datetime, None] = None
    scd_end: Union[datetime, None] = None
    scd_active: Union[bool, None] = None

    
class ZoneListView(Zone):
    geometry: ClassVar[Union[Geometry, None]] = None
    json_data: ClassVar[Union[dict, None]] = None
