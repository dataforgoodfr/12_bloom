from contextlib import AbstractContextManager
from typing import Any, List, Union, Optional

from bloom.domain.zone import Zone, ZoneListView, ZoneSummary
from bloom.domain.zone_category import ZoneCategory
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session
from bloom.dependencies import RangeHeader, PaginatedSqlResult
from sqlalchemy.sql.expression import ScalarSelect, and_, or_, func, text, distinct


class ZoneRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_zone_by_id(self, session: Session, zone_id: int) -> Union[Zone, None]:
        return ZoneRepository.map_to_domain(session.get(sql_model.Zone, zone_id))

    def get_all_zones(self,
                      session: Session,
                      range: Optional[RangeHeader | None] = None)\
                        -> PaginatedSqlResult[list[Zone]]:
        # requête de base
        query=session.query(sql_model.Zone)
        total=session.query(func.count()).select_from(sql_model.Zone)
        print(total)
        # obtention du résultat paginé, format Pydantif grâce à la fonction de
        # de conversion map_to_domain fournie
        # spécification de la pagination fournie par range:RangeSet
        result=PaginatedSqlResult[list[Zone]](session=session,
                                              query=query,
                                              query_total=total,
                                              range=range,
                                              map_to_domain=lambda row: ZoneRepository.map_to_domain(row[0]))
        return result

    def get_all_zones_summary(  self,
                                session: Session,
                                range: Optional[RangeHeader | None] = None)\
                                    -> PaginatedSqlResult[list[ZoneSummary]]:
        q = session.query(
                          sql_model.Zone.id,
                          sql_model.Zone.category,
                          sql_model.Zone.sub_category,
                          sql_model.Zone.name,
                          sql_model.Zone.created_at
                          )
        total=session.query(func.count()).select_from(sql_model.Zone)
        result=PaginatedSqlResult[list[Zone]](session=session,
                                              query=q,
                                              query_total=total,
                                              range=range,
                                              map_to_domain=lambda row: ZoneSummary(id=row[0],
                                                                                    category=row[1],
                                                                                    sub_category=row[2],
                                                                                    name=row[3],
                                                                                    created_at=row[4]
                                                                                    ))
        return result

    def get_all_zone_categories(self,
                                session: Session,
                                range=range,) -> PaginatedSqlResult[list[ZoneCategory]]:
        query = session.query(sql_model.Zone.category,sql_model.Zone.sub_category).distinct()
        total = session.query(func.count(distinct(func.concat(sql_model.Zone.category,'/',sql_model.Zone.sub_category))))
        return PaginatedSqlResult[list[Zone]](session=session,
                                              query=query,
                                              query_total=total,
                                              range=range,
                                              map_to_domain=lambda xy: ZoneCategory(category=xy[0],sub_category=xy[1]))

    def get_all_zones_by_category(self, session: Session, category: str = None, sub: str = None) -> list[Zone]:
        q = session.query(sql_model.Zone)
        if category:
            q = q.filter(sql_model.Zone.category == category)
        if sub:
            q = q.filter(sql_model.Zone.sub_category == sub)
        if not q:
            return []
        return [ZoneRepository.map_to_domain(entity) for entity in session.execute(q).scalars()]

    def batch_create_zone(self, session: Session, zones: list[Zone]) -> list[Zone]:
        orm_list = [ZoneRepository.map_to_orm(zone) for zone in zones]
        session.add_all(orm_list)
        return [ZoneRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_orm(zone: Zone) -> sql_model.Zone:
        return sql_model.Zone(
            id=zone.id,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            geometry=from_shape(zone.geometry),
            centroid=from_shape(zone.centroid),
            json_data=zone.json_data,
            created_at=zone.created_at,
        )

    @staticmethod
    def map_to_domain(zone: sql_model.Zone) -> Zone:
        return Zone(
            id=zone.id,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            geometry=to_shape(zone.geometry),
            centroid=to_shape(zone.centroid),
            json_data=zone.json_data,
            created_at=zone.created_at,
        )

    @staticmethod
    def map_to_summary(zone: sql_model.Zone) -> ZoneSummary:
        return ZoneSummary(
            id=zone.id,
            category=zone.category,
            sub_category=zone.sub_category,
            name=zone.name,
            created_at=zone.created_at,
        )

    @staticmethod
    def map_zonecategory_to_domain(category: ZoneCategory) -> ZoneCategory:
        return ZoneCategory(
            category=category.category,
            sub_category=category.sub_category
        )
