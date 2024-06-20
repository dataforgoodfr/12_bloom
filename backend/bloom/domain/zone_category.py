from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict
from shapely import Geometry, Point, MultiPolygon,Polygon
from shapely.geometry import mapping, shape


class ZoneCategory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    category: str
    sub_category: Union[str, None]
