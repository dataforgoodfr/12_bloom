from datetime import datetime

from pydantic import BaseModel

from typing import Union


class VesselData(BaseModel):
    id: int | None = None
    timestamp: datetime
    ais_class: str | None
    flag: str | None
    name: str | None
    callsign: str | None
    timestamp: datetime | None
    update_timestamp: datetime | None
    ship_type: str | None
    sub_ship_type: str | None
    mmsi: int | None
    imo: int | None
    width: int | None
    length: int | None
    vessel_id: int
    created_at: Union[datetime, None] = None
