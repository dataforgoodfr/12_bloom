from contextlib import AbstractContextManager
from typing import Any, List, Union

from bloom.domain.zone import Zone
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.orm import Session


class ZoneRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_zone_by_id(self, session: Session, zone_id: int) -> Union[Zone, None]:
        return ZoneRepository.map_to_domain(session.get(sql_model.Zone, zone_id))

    def get_all_zones(self, session: Session) -> List[Zone]:
        q = session.query(sql_model.Zone)
        if not q:
            return []
        return [ZoneRepository.map_to_domain(entity) for entity in q]
    
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
