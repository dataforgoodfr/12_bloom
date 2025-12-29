from contextlib import AbstractContextManager
from typing import Any, List, Union, Optional
from datetime import datetime

from bloom.config import settings
from bloom.domain.zone import Zone, ZoneListView, ZoneSummary
from bloom.domain.zone_category import ZoneCategory
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session
from bloom.routers.requests import RangeHeader, PaginatedResult, NonPaginatedResult
from sqlalchemy.sql.expression import ScalarSelect, and_, or_, func, text, select, between


class ZoneRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_zone_by_id(self, session: Session, zone_id: int) -> Union[Zone, None]:
        return ZoneRepository.map_to_domain(session.get(sql_model.Zone, zone_id))
    
    def get_zone_by_key(self, session: Session,
                        key: str,
                        scd_date:Optional[datetime]=None,
                        scd_enable:bool=True
                        )-> Union[Zone,list[Zone],None]:
        stmt=select(sql_model.Zone).where(sql_model.Zone.key == key)
        if scd_enable:
            if scd_date:
                stmt=stmt.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
            else:
                stmt=stmt.where(sql_model.Zone.scd_active)
            return ZoneRepository.map_to_domain(session.execute(stmt).scalar())
        else:
            return ZoneRepository.map_to_domain(session.execute(stmt).scalars())

    def get_all_zones(self, session: Session,
                      range: Optional[RangeHeader | None] = None,
                      scd_date:Optional[datetime]=None,
                      scd_enable:bool=True
                      ) -> PaginatedResult[
        list[Zone]]:

        # q = session.execute(q)
        payload = []
        if range is not None:
            base_query = session.query(sql_model.Zone, func.count().over().label('total'))

            # SCD attribute management
            if scd_enable:
                if scd_date:
                    base_query=base_query.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
                else:
                    base_query=base_query.where(sql_model.Zone.scd_active)

            # Getting total count of model table to evaluate validity of ranges
            total_query = session.query(func.count().label('total')).select_from(sql_model.Zone)
            total_count = session.execute(total_query).scalar_one_or_none()
            for i, spec in enumerate(range.spec):
                paginated = base_query
                if spec.start != None: paginated = paginated.offset(spec.start)
                if spec.end != None and spec.start != None: paginated = paginated.limit(spec.end + 1 - spec.start)
                if spec.end != None and spec.start == None: paginated = paginated.offset(total_count - spec.end).limit(
                    spec.end)

                results = session.execute(paginated).all()
                total = results[0][1] if len(results) > 0 else 0
                payload.extend([ZoneRepository.map_to_domain(model[0]).model_dump() for model in results])
                if spec.end == None: range.spec[i].end = total - 1
            return PaginatedResult[list[Zone]](payload=payload, total=total, spec=range.spec, unit=range.unit)
        else:
            # SCD attribute management
            query=session.query(sql_model.Zone)
            if scd_enable:
                if scd_date:
                    query=query.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
                else:
                    query=query.where(sql_model.Zone.scd_active)
            payload = [ZoneRepository.map_to_domain(model).model_dump()
                       for model in session.execute(query).scalars()]
            return PaginatedResult[list[Zone]](payload=payload)

    def get_all_zones_summary(self, session: Session,
                      scd_date:Optional[datetime]=None,
                      scd_enable:bool=True
                      ) -> list[ZoneSummary]:
        q = session.query(
            sql_model.Zone.id,
            sql_model.Zone.category,
            sql_model.Zone.sub_category,
            sql_model.Zone.name,
            sql_model.Zone.created_at,
            sql_model.Zone.enable,
        )
        if scd_enable:
            if scd_date:
                q=q.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
            else:
                q=q.where(sql_model.Zone.scd_active)
        
        if not q:
            return []
        return [ZoneRepository.map_to_summary(entity) for entity in q.all()]

    def get_all_zone_categories(self, session: Session,
                      scd_date:Optional[datetime]=None,
                      scd_enable:bool=True) -> list[ZoneCategory]:
        q = session.query(sql_model.Zone.category,
                          sql_model.Zone.sub_category).distinct()
        # SCD attribute management
        if scd_enable:
            if scd_date:
                q=q.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
            else:
                q=q.where(sql_model.Zone.scd_active)
        q = session.execute(q)
        if not q:
            return []
        return [ZoneRepository.map_zonecategory_to_domain(ZoneCategory(category=cat, sub_category=sub)) for cat, sub in
                q]

    def get_all_zones_by_category(self, session: Session,
                                  category: str = None, sub: str = None,
                                  scd_date:Optional[datetime]=None,
                                  scd_enable:bool=True
                                  ) -> list[Zone]:
        q = session.query(sql_model.Zone)
        if category:
            q = q.filter(sql_model.Zone.category == category)
        if sub:
            q = q.filter(sql_model.Zone.sub_category == sub)
        # SCD attribute management
        if scd_enable:
            if scd_date:
                q=q.where(between(scd_date,sql_model.Zone.scd_start,sql_model.Zone.scd_end))
            else:
                q=q.where(sql_model.Zone.scd_active)
        if not q:
            return []
        return [ZoneRepository.map_to_domain(entity) for entity in session.execute(q).scalars()]

    def batch_create_zone(self, session: Session, zones: list[Zone]) -> list[Zone]:
        orm_list = [ZoneRepository.map_to_orm(zone) for zone in zones]

        # SCD attributes management initialization
        # Consider new vessel valid and active on all scd interval
        # from settings.scd_past_limit to settings.scd_future_limit
        for zone in orm_list:
            zone.scd_active = True
            zone.scd_start = settings.scd_past_limit
            zone.scd_end = settings.scd_future_limit

        session.add_all(orm_list)
        return [ZoneRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_orm(zone: Zone) -> sql_model.Zone:
        return sql_model.Zone(
            id=zone.id,
            key=zone.key,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            geometry=from_shape(zone.geometry),
            centroid=from_shape(zone.centroid),
            json_data=zone.json_data,
            created_at=zone.created_at,
            enable=zone.enable,
            scd_start=zone.scd_start,
            scd_end=zone.scd_end,
            scd_active=zone.scd_active,
        )

    @staticmethod
    def map_to_domain(zone: sql_model.Zone) -> Zone:
        return Zone(
            id=zone.id,
            key=zone.key,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            geometry=to_shape(zone.geometry),
            centroid=to_shape(zone.centroid),
            json_data=zone.json_data,
            created_at=zone.created_at,
            enable=zone.enable,
            scd_start=zone.scd_start,
            scd_end=zone.scd_end,
            scd_active=zone.scd_active,
        )

    @staticmethod
    def map_to_summary(zone: sql_model.Zone) -> ZoneSummary:
        return ZoneSummary(
            id=zone.id,
            key=zone.key,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            created_at=zone.created_at,
            enable=zone.enable,
            scd_start=zone.scd_start,
            scd_end=zone.scd_end,
            scd_active=zone.scd_active,
        )

    @staticmethod
    def map_zonecategory_to_domain(category: ZoneCategory) -> ZoneCategory:
        return ZoneCategory(
            category=category.category,
            sub_category=category.sub_category
        )
