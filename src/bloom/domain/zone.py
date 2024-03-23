from datetime import datetime

from pydantic import BaseModel
from shapely import Point, Polygon

from typing import Union


class Zone(BaseModel):
    id: int | None = None
    category: str
    sub_category: Union[str, None] = None
    name: str
    geometry: Union[Polygon, None] = None
    centroid: Union[Point, None] = None
    json_data: Union[dict, None] = None
    created_at: Union[ datetime , None] = None
    updated_at: Union[ datetime , None] = None
