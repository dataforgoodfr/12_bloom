from datetime import datetime

from pydantic import BaseModel

from typing import Union


class VesselVoyage(BaseModel):
    id: int | None = None
    timestamp: datetime
    destination: str | None
    draught: float | None
    eta: datetime | None
    vessel_id: int
    created_at: Union[datetime, None] = None
