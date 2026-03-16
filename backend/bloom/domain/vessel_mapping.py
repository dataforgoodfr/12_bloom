from datetime import datetime
from typing import Optional, ClassVar
from .vessel import VesselListView

from pydantic import BaseModel


class VesselMapping(BaseModel):
    id:             Optional[int] = None
    imo:            Optional[int] = None
    mmsi:           Optional[int] = None
    name:           Optional[str] = None
    country:        Optional[str] = None

    same_imo:       Optional[list[int]] = None
    same_mmsi:      Optional[list[int]] = None
    same_name:      Optional[list[int]] = None
    same_country:   Optional[list[int]] = None
    
    appearance_first:Optional[datetime] = None
    appearance_last:Optional[datetime] = None
    
    mapping_auto:   Optional[VesselListView] = None
    mapping_manual: Optional[VesselListView] = None
    vessel:         Optional[VesselListView] = None

    scd_start:      Optional[datetime] = None
    scd_end:        Optional[datetime] = None
    scd_active:     Optional[bool] = None
