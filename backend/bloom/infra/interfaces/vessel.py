from .repository import AbstractRepository
import abc
from typing import TypeVar, Generic, Optional, List
from datetime import datetime

DOMAIN=TypeVar("DOMAIN")

class AbstractVesselRepository(AbstractRepository[DOMAIN],Generic[DOMAIN]):
    pass

class AbstractVesselMappingRepository(AbstractRepository[DOMAIN],Generic[DOMAIN]):
    def get(
        imo:Optional[int]=None,
        mmsi:Optional[int]=None,
        country:Optional[int]=None,
        scd_date:Optional[datetime]=None
        ):
        pass