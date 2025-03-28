from datetime import datetime
from typing import Union, ClassVar

from pydantic import BaseModel


class VesselMapping(BaseModel):
    id: Union[int, None] = None
    mmsi: Union[int, None] = None
    imo: Union[int, None] = None
    ship_name: Union[str, None] = None
    vessel_id: Union[int, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None