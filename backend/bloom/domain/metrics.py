from pydantic import BaseModel, ConfigDict
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from bloom.domain.vessel import Vessel,VesselListView
from bloom.domain.zone import Zone,ZoneListView
from typing import Union

class Metrics(BaseModel) :
    model_config = ConfigDict(arbitrary_types_allowed=True)
    timestamp : datetime
    vessel_id: int
    type : str
    vessel_mmsi: int
    ship_name: str
    vessel_country_iso3: str 
    vessel_imo: int
    duration_total : timedelta
    duration_fishing: Optional[timedelta] = None
    zone_name : str
    zone_id : Optional[int] = None
    zone_category : Optional[str] = None
    zone_sub_category : Optional[str] = None
    zone_enable: Optional[bool] = None

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

class ResponseMetricsVesselInZonesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vessel: VesselListView
    total_time_in_zones: Optional[timedelta]

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


class VesselTimeInZone(BaseModel):
    vessel_id: Optional[int] = None
    zone_id: Optional[int] = None
    zone_name: Optional[str] = None
    zone_category: Optional[str] = None
    zone_sub_category: Optional[str] = None
    duration_total: Optional[timedelta] = None
    duration_fishing: Optional[timedelta] = None
