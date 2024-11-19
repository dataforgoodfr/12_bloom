from datetime import datetime
from typing import Union

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
    category: str
    sub_category: Union[str, None] = None
    name: str
    geometry: Union[Geometry, None] = None
    centroid: Union[Point, None] = None
    beneficiaries: Union[str, None] = None
    json_data: Union[dict, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
