from contextlib import AbstractContextManager
from typing import Union

from bloom.domain.vessel import Vessel
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy import func, select, update, and_
from sqlalchemy.orm import Session

from bloom.infra.repository import GenericRepository, GenericSqlRepository
from abc import ABC, abstractmethod

from bloom.domain.vessel import Vessel
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable


class VesselRepositoryBase(GenericRepository[Vessel], ABC):
    @abstractmethod
    def set_tracking(self, vessel_ids: list[int], tracking_activated: bool,
                     tracking_status: str) -> None:
        raise NotImplementedError()
    def check_mmsi_integrity(self) -> list[(int, int)]:
        raise NotImplementedError()

class VesselRepository(GenericSqlRepository[Vessel,sql_model.Vessel],VesselRepositoryBase):
    def __init__(self,session:Session) -> None:
        super().__init__(session=session,model_cls=sql_model.Vessel, schema_cls=Vessel)

    def set_tracking(self, vessel_ids: list[int], tracking_activated: bool,
                     tracking_status: str) -> None:
        updates = [{"id": id, "tracking_activated": tracking_activated, "tracking_status": tracking_status} for id in
                   vessel_ids]
        self._session.execute(update(sql_model.Vessel), updates)
        
    def check_mmsi_integrity(self) -> list[(int, int)]:
        # Recherche des valeurs distinctes de MMSI ayant un nombre de résultats actif > 1
        stmt = select(sql_model.Vessel.mmsi, func.count(sql_model.Vessel.id).label("count")).group_by(
            sql_model.Vessel.mmsi).having(
            func.count(sql_model.Vessel.id) > 1).where(
            sql_model.Vessel.tracking_activated == True)
        return self._session.execute(stmt).all()
    
    def map_to_domain(self, model: sql_model.Vessel) -> Vessel:
         return Vessel(
            id=model.id,
            mmsi=model.mmsi,
            ship_name=model.ship_name,
            width=model.width,
            length=model.length,
            country_iso3=model.country_iso3,
            type=model.type,
            imo=model.imo,
            cfr=model.cfr,
            external_marking=model.external_marking,
            ircs=model.ircs,
            tracking_activated=model.tracking_activated,
            tracking_status=model.tracking_status,
            home_port_id=model.home_port_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            details=model.details,
            check=model.check,
            length_class=model.length_class,
         )

    def map_to_model(self, schema: Vessel) -> sql_model.Vessel:
         return sql_model.Vessel(**schema.__dict__)


"""
class VesselRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_vessel_by_id(self, session: Session, vessel_id: int) -> Union[Vessel, None]:
        return session.get(sql_model.Vessel, vessel_id)

    def get_activated_vessel_by_mmsi(self, session: Session, mmsi: int) -> Union[Vessel, None]:
        stmt = select(sql_model.Vessel).where(
            and_(
                sql_model.Vessel.tracking_activated == True,
                sql_model.Vessel.mmsi == mmsi
            )
        )
        vessel = session.execute(stmt).scalar()
        if not vessel:
            return None
        else:
            return VesselRepository.map_to_domain(vessel)

    def get_vessels_list(self, session: Session) -> list[Vessel]:
        """"""
        Liste l'ensemble des vessels actifs
        """"""
        stmt = select(sql_model.Vessel).where(sql_model.Vessel.tracking_activated == True)
        e = session.execute(stmt).scalars()
        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    def get_all_vessels_list(self, session: Session) -> list[Vessel]:
        """"""
        Liste l'ensemble des vessels actifs ou inactifs
        """"""
        stmt = select(sql_model.Vessel)
        e = session.execute(stmt).scalars()

        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    def batch_create_vessel(self, session: Session, vessels: list[Vessel]) -> list[Vessel]:
        orm_list = [VesselRepository.map_to_sql(port) for port in vessels]
        session.add_all(orm_list)
        return [VesselRepository.map_to_domain(orm) for orm in orm_list]

    def batch_update_vessel(self, session: Session, vessels: list[Vessel]) -> None:
        updates = [{"id": v.id, "mmsi": v.mmsi, "ship_name": v.ship_name, "width": v.width, "length": v.length,
                    "country_iso3": v.country_iso3, "type": v.type, "imo": v.imo, "cfr": v.cfr,
                    "external_marking": v.external_marking,
                    "ircs": v.ircs, "tracking_activated": v.tracking_activated, "tracking_status": v.tracking_status,
                    "home_port_id": v.home_port_id} for v in
                   vessels]
        session.execute(update(sql_model.Vessel), updates)

    def set_tracking(self, session: Session, vessel_ids: list[int], tracking_activated: bool,
                     tracking_status: str) -> None:
        updates = [{"id": id, "tracking_activated": tracking_activated, "tracking_status": tracking_status} for id in
                   vessel_ids]
        session.execute(update(sql_model.Vessel), updates)

    def check_mmsi_integrity(self, session: Session) -> list[(int, int)]:
        # Recherche des valeurs distinctes de MMSI ayant un nombre de résultats actif > 1
        stmt = select(sql_model.Vessel.mmsi, func.count(sql_model.Vessel.id).label("count")).group_by(
            sql_model.Vessel.mmsi).having(
            func.count(sql_model.Vessel.id) > 1).where(
            sql_model.Vessel.tracking_activated == True)
        return session.execute(stmt).all()

    @staticmethod
    def map_to_domain(model: sql_model.Vessel) -> Vessel:
        return Vessel(
            id=model.id,
            mmsi=model.mmsi,
            ship_name=model.ship_name,
            width=model.width,
            length=model.length,
            country_iso3=model.country_iso3,
            type=model.type,
            imo=model.imo,
            cfr=model.cfr,
            external_marking=model.external_marking,
            ircs=model.ircs,
            tracking_activated=model.tracking_activated,
            tracking_status=model.tracking_status,
            home_port_id=model.home_port_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            details=model.details,
            check=model.check,
            length_class=model.length_class,
        )

    @staticmethod
    def map_to_sql(vessel: Vessel) -> sql_model.Vessel:
        return sql_model.Vessel(
            id=vessel.id,
            mmsi=vessel.mmsi,
            ship_name=vessel.ship_name,
            width=vessel.width,
            length=vessel.length,
            country_iso3=vessel.country_iso3,
            type=vessel.type,
            imo=vessel.imo,
            cfr=vessel.cfr,
            external_marking=vessel.external_marking,
            ircs=vessel.ircs,
            tracking_activated=vessel.tracking_activated,
            tracking_status=vessel.tracking_status,
            home_port_id=vessel.home_port_id,
            created_at=vessel.created_at,
            updated_at=vessel.updated_at,
            details=vessel.details,
            check=vessel.check,
            length_class=vessel.length_class,
        )
    """