from datetime import datetime
from typing import Union

from pydantic import BaseModel
from shapely import Geometry


class WhiteZone(BaseModel):
    id: Union[ int | None ] = None
    geometry: Union[Geometry, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
