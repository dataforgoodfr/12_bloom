from contextlib import AbstractContextManager
from typing import Any, Generator, Union, Optional
from datetime import datetime

from bloom.domain.vessel_mapping import VesselMapping
from bloom.domain.metrics import VesselTimeInZone
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy import (func, select, update, and_, asc, desc, literal_column,
                        between, bindparam)
from sqlalchemy.orm import Session
from bloom.routers.requests import (DatetimeRangeRequest,
                                    OrderByRequest,
                                    OrderByEnum)
from bloom.config import settings
from bloom.infra.interfaces.repository import (AbstractRepository,
                                          construct_findBy_scd_statement,
                                          exclude_keys
)
from bloom.infra.interfaces.vessel import (AbstractVesselMappingRepository)
from bloom.infra.repositories.repository_vessel import VesselRepository


class VesselMappingRepository(AbstractVesselMappingRepository[VesselMapping]):
    session:Session
    def __init__(self, session:Session):
        self.session=session

    def findBy(self,
               offset=None,
               limit=None,
               scd_date:Optional[datetime]=None,
               **filters):
        stmt = construct_findBy_scd_statement(sql_model.Vessel,
                                        offset=offset,
                                        limit=limit,
                                        scd_date=scd_date,
                                        **filters)
        return [v for v in self.session.execute(stmt).scalars()]
    

    @staticmethod
    def map_to_domain(model: sql_model.VesselMapping) -> VesselMapping:
        return VesselMapping(
            id=model.id,
            imo=model.imo,
            mmsi=model.mmsi,
            name=model.name,
            country=model.country,

            same_imo=model.same_imo,
            same_mmsi=model.same_mmsi,
            same_name=model.same_name,
            same_country=model.same_country,

            appearance_first=model.appearance_first,
            appearance_last=model.appearance_last,
            
            mapping_auto=model.mapping_auto,
            mapping_manual=model.mapping_manual,
            vessel=VesselRepository.map_to_domain(model.vessel),

            scd_start=model.scd_start,
            scd_end=model.scd_end,
            scd_active=model.scd_active,
        )

    @staticmethod
    def map_to_sql(vessel: VesselMapping) -> sql_model.VesselMapping:
        return sql_model.VesselMapping(
            id=vessel.id,
            imo=vessel.imo,
            mmsi=vessel.mmsi,
            name=vessel.name,
            country=vessel.country,

            same_imo=vessel.same_imo,
            same_mmsi=vessel.same_mmsi,
            same_name=vessel.same_name,
            same_country=vessel.same_country,

            appearance_first=vessel.appearance_first,
            appearance_last=vessel.appearance_last,

            vessel=VesselRepository.map_to_sql(vessel.vessel),

            scd_start=vessel.scd_start,
            scd_end=vessel.scd_end,
            scd_active=vessel.scd_active,
        )
