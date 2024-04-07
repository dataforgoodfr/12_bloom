from datetime import datetime

from pydantic import BaseModel

from typing import Union


class VesselData(BaseModel):
    id: Union[ int , None ]
    timestamp: datetime
    ais_class:  Union[str , None]
    flag:  Union[str , None]
    name:  Union[str , None]
    callsign:  Union[str , None]
    timestamp:  Union[datetime , None]
    ship_type:  Union[str , None]
    sub_ship_type:  Union[str , None]
    mmsi:  Union[int , None]
    imo:  Union[int , None]
    width:  Union[int , None]
    length:  Union[int , None]
    vessel_id: int
    created_at: Union[datetime, None]

    def __init__(self):
        self.id = None
        self.created_at = None