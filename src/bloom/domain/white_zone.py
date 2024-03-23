from datetime import datetime

from pydantic import BaseModel
from shapely import Point, Polygon

from typing import Union


class WhiteZone(BaseModel):
    id: int | None = None
    geometry: Union[Polygon, None] = None
    created_at: Union[ datetime , None] = None
    updated_at: Union[ datetime , None] = None
