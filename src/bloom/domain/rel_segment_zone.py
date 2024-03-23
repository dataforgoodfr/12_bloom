from datetime import datetime, timedelta

from pydantic import BaseModel

from typing import Union


class RelSegmentZone(BaseModel):
    segment_id: int
    zone_id: int
    created_at: Union[datetime, None] = None
