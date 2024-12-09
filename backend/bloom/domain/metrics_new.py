from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta

class Metrics(BaseModel) :
    model_config = ConfigDict(arbitrary_types_allowed=True)
    timestamp : datetime
    vessel_id: Optional[int]
    vessel_mmsi: int
    ship_name: str
    type : str
    duration_total : int
    duration_fishing: Optional[int] = None
    mpa_name : Optional[str] = None

