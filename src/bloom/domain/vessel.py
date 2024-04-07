from datetime import datetime
from typing import Union

from pydantic import BaseModel


class Vessel(BaseModel):
    id: Union[int, None] = None
    mmsi: Union[int, None]
    ship_name: str
    width: Union[float, None] = None
    length: Union[float, None] = None
    country_iso3: str
    type: str
    imo: Union[int, None]
    cfr: Union[str, None]
    registration_number: Union[str, None]
    external_marking: Union[str, None]
    ircs: Union[str, None]
    tracking_activated: Union[bool, None] = None
    tracking_status: Union[str, None] = None
    home_port_id: Union[int, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    comment: str
