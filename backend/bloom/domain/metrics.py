from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from bloom.domain.vessel import Vessel

class TotalTimeActivityTypeEnum(str, Enum):
    total_time_at_sea: str = "Total Time at Sea"
    total_time_in_amp: str = "Total Time in AMP"
    total_time_in_territorial_waters: str = "Total Time in Territorial Waters"
    total_time_in_zones_with_no_fishing_rights: str = "Total Time in zones with no fishing rights"
    total_time_fishing: str = "Total Time Fishing"
    total_time_fishing_in_amp: str = "Total Time Fishing in AMP"
    total_time_fishing_in_territorial_waters: str = "Total Time Fishing in Territorial Waters"
    total_time_fishing_in_zones_with_no_fishing_rights: str = "Total Time Fishing in zones with no fishing rights"
    total_time_fishing_in_extincting_amp: str = "Total Time in Extincting AMP"

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