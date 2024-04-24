from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict
from shapely import Geometry, Point


class Zone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: Union[int, None] = None
    category: str
    sub_category: Union[str, None] = None
    name: str
    geometry: Union[Geometry, None] = None
    centroid: Union[Point, None] = None
    json_data: Union[dict, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
