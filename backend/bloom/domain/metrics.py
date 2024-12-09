from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from bloom.domain.vessel import Vessel,VesselListView
from bloom.domain.zone import Zone,ZoneListView

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
    zone_name : str
    
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
    vessel: VesselListView
    total_time_at_sea: Optional[timedelta]

class ResponseMetricsZoneVisitedSchema(BaseModel):
    zone: ZoneListView
    visiting_duration: timedelta

class ResponseMetricsZoneVisitingTimeByVesselSchema(BaseModel):
    zone: ZoneListView
    vessel: VesselListView
    zone_visiting_time_by_vessel: timedelta


class ResponseMetricsVesselVisitingTimeByZoneSchema(BaseModel):
    zone: ZoneListView
    vessel: VesselListView
    vessel_visiting_time_by_zone: timedelta

class ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema(BaseModel):
    vessel_id : int
    activity: str
    total_activity_time: timedelta



class TotalTimeActivityTypeRequest(BaseModel):
    type: TotalTimeActivityTypeEnum