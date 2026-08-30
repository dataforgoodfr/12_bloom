from contextlib import AbstractContextManager
from typing import Any, Generator, Union

from bloom.domain.vessel import Vessel
from bloom.domain.metrics import VesselTimeInZone
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy import func, select, update, insert, and_, asc, desc, literal_column
from sqlalchemy.orm import Session
from bloom.routers.requests import (DatetimeRangeRequest,
                                    OrderByRequest,
                                    OrderByEnum)
from bloom.domain.vessel_mapping import VesselMapping


class VesselMappingRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory


    def findBy(self,
            session: Session,
            mmsi:str=None,
            imo:int=None,
            ship_name:str=None) -> list[VesselMapping]:
        stmt= (select(VesselMapping)
               .select_from(sql_model.VesselMapping))
        if mmsi:
               stmt=stmt.where(sql_model.VesselMapping.mmsi == mmsi)
        if imo:
               stmt=stmt.where(sql_model.VesselMapping.imo == imo)
        if ship_name:
               stmt=stmt.where(sql_model.VesselMapping.ship_name == ship_name)
        return session.execute(stmt).scalar()

    def add(self,
            session: Session,
            mmsi:str=None,
            imo:int=None,
            ship_name:str=None,
            vessel_id:int=None
            ):
        stmt=insert(sql_model.VesselMapping,[
            {
            "mmsi": mmsi,
            "imo": imo,
            "ship_name": ship_name,
            "vessel_id": vessel_id,
            }])
        return session.execute(stmt)