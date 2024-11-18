from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from bloom.domain.vessel import Vessel
from bloom.domain.zone import ZoneIdent

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
    vessel: Vessel
    total_time_at_sea: Optional[timedelta]

class ResponseMetricsZoneVisitedSchema(BaseModel):
    zone: ZoneIdent
    visiting_duration: timedelta

class ResponseMetricsZoneVisitingTimeByVesselSchema(BaseModel):
    zone: ZoneIdent
    vessel: Vessel
    zone_visiting_time_by_vessel: timedelta

class ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema(BaseModel):
    vessel_id : int
    activity: str
    total_activity_time: timedelta



class TotalTimeActivityTypeRequest(BaseModel):
    type: TotalTimeActivityTypeEnum