from datetime import datetime

from pydantic import BaseModel

from typing import Union


class VesselVoyage(BaseModel):
    id: int | None = None
    timestamp: datetime
    voyage_destination: str | None
    voyage_draught: float | None
    voyage_eta: datetime | None
    vessel_id: int
    created_at: Union[datetime, None] = None
