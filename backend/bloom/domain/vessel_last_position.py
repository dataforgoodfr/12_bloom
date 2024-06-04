from datetime import datetime

from pydantic import BaseModel, ConfigDict
from shapely import Geometry, Point
from shapely.geometry import mapping, shape
from bloom.domain.vessel import Vessel
from bloom.domain.port import Port

from typing import Union


class VesselLastPosition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True,
        json_encoders = {
                Geometry: lambda p: mapping(p),
            },)
    vessel: Vessel = None
    excursion_id: Union[int, None] = None
    position: Union[Point, None] = None
    timestamp: Union[datetime, None] = None
    heading: Union[float, None] = None
    speed: Union[float, None] = None
    arrival_port: Union[Port, None] = None
