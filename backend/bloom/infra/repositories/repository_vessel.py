from contextlib import AbstractContextManager
from typing import Any, Generator, Union, Optional
from datetime import datetime

from bloom.domain.vessel import Vessel
from bloom.domain.metrics import VesselTimeInZone
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy import func, select, update, and_, asc, desc, literal_column, between
from sqlalchemy.orm import Session
from bloom.routers.requests import (DatetimeRangeRequest,
                                    OrderByRequest,
                                    OrderByEnum)
from bloom.config import settings


class VesselRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory


    def get_vessel_tracked_count(self, session: Session,
                                 scd_date:Optional[datetime]=None,
                                 scd_enable:bool=True
                                 ) -> int:
        stmt = select(func.count(sql_model.Vessel.id)).select_from(sql_model.Vessel)\
            .distinct().where(sql_model.Vessel.tracking_activated == True)
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        return session.execute(stmt).scalar()

    def get_vessel_types(self,
                         session: Session,
                         scd_date:Optional[datetime]=None,
                         scd_enable:bool=True
                        ) -> list[str]:
        stmt = select(sql_model.Vessel.type).select_from(sql_model.Vessel).distinct()
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        return [i for i in session.execute(stmt).scalars()]
    
    def get_vessel_length_classes(self, session: Session,
                         scd_date:Optional[datetime]=None,
                         scd_enable:bool=True
                         ) -> list[str]:
        stmt = select(sql_model.Vessel.length_class).select_from(sql_model.Vessel).distinct()
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        return [i for i in session.execute(stmt).scalars()]
    
    def get_vessel_countries(self, session: Session,
                         scd_date:Optional[datetime]=None,
                         scd_enable:bool=True
                         ) -> list[str]:
        stmt = select(sql_model.Vessel.country_iso3).select_from(sql_model.Vessel).distinct()
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        return [i for i in session.execute(stmt).scalars()]

    def get_vessel_by_id(self, session: Session, vessel_id: int) -> Union[Vessel, None]:
        return session.get(sql_model.Vessel, vessel_id)
    
    def get_vessel_by_key(self, session: Session,
                          key: str,
                          scd_date:Optional[datetime]=None,
                          scd_enable:bool=True
                         ) -> Union[Vessel, list[Vessel],None]:
        stmt=select(sql_model.Vessel).where(sql_model.Vessel.key == key)
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
            return session.execute(stmt).scalar()
        else:
            return session.execute(stmt).scalars()

    def get_activated_vessel_by_mmsi(self, session: Session,
                                     mmsi: int,
                                     scd_date:Optional[datetime]=None,
                                     scd_enable:bool=True
                                     ) -> Union[Vessel, None]:
        stmt = select(sql_model.Vessel).where(
            and_(
                sql_model.Vessel.tracking_activated == True,
                sql_model.Vessel.mmsi == mmsi
            )
        )
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        vessel = session.execute(stmt).scalar()
        if not vessel:
            return None
        else:
            return VesselRepository.map_to_domain(vessel)

    def get_vessels_list(self, session: Session,
                         scd_date:Optional[datetime]=None,
                         scd_enable:bool=True
                         ) -> list[Vessel]:
        """
        Liste l'ensemble des vessels actifs
        """
        stmt = select(sql_model.Vessel).where(sql_model.Vessel.tracking_activated == True)
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        e = session.execute(stmt).scalars()
        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    def get_all_vessels_list(self,
                             session: Session,
                             scd_date:Optional[datetime]=None,
                             scd_enable:bool=True
                             ) -> list[Vessel]:
        """
        Liste l'ensemble des vessels actifs ou inactifs
        """
        stmt = select(sql_model.Vessel)
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Vessel.scd_start,sql_model.Vessel.scd_end))
            else:
                stmt=stmt.where(sql_model.Vessel.scd_active)
        e = session.execute(stmt).scalars()

        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    
    def get_vessel_times_in_zones(  self,
                                    session: Session,
                                    vessel_id: int,
                                    datetime_range: DatetimeRangeRequest,
                                    order: OrderByRequest,
                                    category: str = None,
                                    sub_cateogry: str = None,
                                  )-> list[VesselTimeInZone]:
        """
        Renvoie le temps passés par zones pour un bateau sur une période donnée
        Paramètres:
        - vessel_id
        - start_at/end_at
        - category
        - sub_category
        Valeurs renvoyées:
        - zone_name: nome de la zone
        - zone_category: categorie de la zone
        - zone_sub_category: sous-categorie de la zone
        - duration_total: durée total dans la zone
        - duration_fishing: durée à pêcher
        """
        stmt = (select(sql_model.Metrics.vessel_id,
                           sql_model.Metrics.zone_id,
                           sql_model.Metrics.zone_name,
                           sql_model.Metrics.zone_category,
                           sql_model.Metrics.zone_sub_category,
                        func.sum(sql_model.Metrics.duration_total).label("duration_total"),
                        func.sum(sql_model.Metrics.duration_fishing).label("duration_fishing"),
                        )
                        .select_from(sql_model.Metrics)
                        .join(sql_model.Zone,sql_model.Zone.id==sql_model.Metrics.zone_id )
                        .where(sql_model.Metrics.vessel_id==vessel_id)
                        .where(sql_model.Zone.enable == True)\
                        .where(sql_model.Metrics.timestamp.between(datetime_range.start_at,datetime_range.end_at))
                ).group_by(sql_model.Metrics.vessel_id,
                           sql_model.Metrics.zone_id,
                           sql_model.Metrics.zone_name,
                           sql_model.Metrics.zone_category,
                           sql_model.Metrics.zone_sub_category
                           )
        
        stmt =  stmt.order_by(asc(literal_column("duration_total")))\
                if  order.order == OrderByEnum.ascending \
                else stmt.order_by(desc(literal_column("duration_total")))
        if(category):
            stmt=stmt.where(sql_model.Metrics.zone_category==category)
        if(sub_cateogry):
            stmt=stmt.where(sql_model.Metrics.zone_sub_category==sub_cateogry)
        
        result = [VesselTimeInZone(
            vessel_id=row[0],
            zone_id=row[1],
            zone_name=row[2],
            zone_category=row[3],
            zone_sub_category=row[4],
            duration_total=row[5],
            duration_fishing=row[6],
        ) for row in session.execute(stmt).all()]
        
        return result

    def batch_create_vessel(self, session: Session,
                            vessels: list[Vessel]
                            ) -> list[Vessel]:
        orm_list = [VesselRepository.map_to_sql(vessel) for vessel in vessels]
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
    def map_to_domain(sql_vessel: sql_model.Vessel) -> Vessel:
        return Vessel(
            id=sql_vessel.id,
            mmsi=sql_vessel.mmsi,
            ship_name=sql_vessel.ship_name,
            width=sql_vessel.width,
            length=sql_vessel.length,
            country_iso3=sql_vessel.country_iso3,
            type=sql_vessel.type,
            imo=sql_vessel.imo,
            cfr=sql_vessel.cfr,
            external_marking=sql_vessel.external_marking,
            ircs=sql_vessel.ircs,
            tracking_activated=sql_vessel.tracking_activated,
            tracking_status=sql_vessel.tracking_status,
            home_port_id=sql_vessel.home_port_id,
            created_at=sql_vessel.created_at,
            updated_at=sql_vessel.updated_at,
            details=sql_vessel.details,
            check=sql_vessel.check,
            length_class=sql_vessel.length_class,
            scd_start=sql_vessel.scd_start,
            scd_end=sql_vessel.scd_end,
            scd_active=sql_vessel.scd_active,
        )

    @staticmethod
    def map_to_sql(vessel: Vessel) -> sql_model.Vessel:
        return sql_model.Vessel(
            id=vessel.id,
            key=vessel.key,
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
            scd_start=vessel.scd_start,
            scd_end=vessel.scd_end,
            scd_active=vessel.scd_active,
        )
