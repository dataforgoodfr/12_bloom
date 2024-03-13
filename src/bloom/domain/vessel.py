from datetime import datetime, timezone

from pydantic import BaseModel, validator
from shapely import Point

from typing import Union


class Vessel(BaseModel):
    vessel_id: int
    ship_name: Union[str, None]
    IMO: Union[str, None]
    mmsi: Union[int, None]

    def get_mmsi(self) -> int:
        return self.mmsi