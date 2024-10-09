from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from bloom.domain.vessel import Vessel
from bloom.dependencies import TotalTimeActivityTypeEnum

class ResponseMetricsVesselInActivitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vessel_id: Optional[int]
    vessel_mmsi: int
    vessel_ship_name: str
    vessel_width: Optional[float] = None
    vessel_length: Optional[float] = None
    vessel_country_iso3: Optional[str] = None
    vessel_type: Optional[str] = None
    vessel_imo: Optional[int] = None
    vessel_cfr: Optional[str] = None
    vessel_external_marking: Optional[str] = None
    vessel_ircs: Optional[str] = None
    vessel_home_port_id: Optional[int] = None
    vessel_details: Optional[str] = None
    vessel_tracking_activated: Optional[bool]
    vessel_tracking_status: Optional[str]
    vessel_length_class: Optional[str]
    vessel_check: Optional[str]
    total_time_at_sea: Optional[timedelta]

class ResponseMetricsZoneVisitedSchema(BaseModel):
    zone_id : int
    zone_category: Optional[str]
    zone_sub_category: Optional[str] = None
    zone_name: str
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

class ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema(BaseModel):
    vessel_id : int
    total_activity_time: timedelta



class TotalTimeActivityTypeRequest(BaseModel):
    type: TotalTimeActivityTypeEnum