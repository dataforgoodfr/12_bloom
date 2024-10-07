from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum

class ResponseMetricsVesselInActivitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mmsi: int
    ship_name: str
    width: Optional[float] = None
    length: Optional[float] = None
    country_iso3: Optional[str] = None
    type: Optional[str] = None
    imo: Optional[int] = None
    cfr: Optional[str] = None
    external_marking: Optional[str] = None
    ircs: Optional[str] = None
    home_port_id: Optional[int] = None
    details: Optional[str] = None
    tracking_activated: Optional[bool]
    tracking_status: Optional[str]
    length_class: Optional[str]
    check: Optional[str]
    total_time_at_sea: timedelta

class ResponseMetricsZoneVisitedSchema(BaseModel):
    id : int
    category: str
    sub_category: Optional[str] = None
    name: str
    visiting_duration: timedelta

class ResponseMetricsZoneVisitingTimeByVesselSchema(BaseModel):
    zone_id : int
    zone_category: str
    zone_sub_category: Optional[str] = None
    zone_name: str
    vessel_id : int
    vessel_name: str
    vessel_type: Optional[str] = None
    vessel_length_class: Optional[str] = None
    zone_visiting_time_by_vessel: timedelta