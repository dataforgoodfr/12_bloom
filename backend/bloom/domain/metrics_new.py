from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta

class Metrics(BaseModel) :
    model_config = ConfigDict(arbitrary_types_allowed=True)
    timestamp : datetime
    vessel_id: int
    type : str
    vessel_mmsi: int
    ship_name: str
    vessel_country_iso3: str 
    vessel_imo: int
    duration_total : float
    duration_fishing: Optional[float] = None
    mpa_name : str

