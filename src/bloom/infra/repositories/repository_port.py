# For python 3.9 syntax compliance
from typing import Union, List

from bloom.domain.port import Port
from bloom.infra.database.sql_model import Port as OrmPort
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from sqlalchemy.orm import Session


class PortRepository:
    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def get_port_by_id(self, port_id: int) -> Union[Port, None]:
        with self.session_factory() as session:
            entity = session.get(OrmPort, port_id)
            if entity is not None:
                return self.map_to_domain(entity)
            else:
                return None

    def get_empty_geometry_buffer_ports(self) -> List[Port]:
        with self.session_factory() as session:
            q = session.query(OrmPort).filter(OrmPort.geometry_buffer == None)
            if not q:
                return []
            return [self.map_to_domain(entity) for entity in q]
        
    def get_all_ports(self) -> List[Port]:
        with self.session_factory() as session:
            q = session.query(OrmPort)
            if not q:
                return []
            return [self.map_to_domain(entity) for entity in q]

    def update_geometry_buffer(self, port_id: int, buffer: Polygon, session: Session) -> Port:
        entity = session.query(OrmPort).get(port_id)
        entity.geometry_buffer = from_shape(buffer)
        if entity is not None:
            return self.map_to_domain(entity)
        else:
            return None

    def create_port(self, port: Port) -> Port:
        orm_port = PortRepository.map_to_sql(port)
        with self.session_factory() as session:
            session.add(orm_port)
            session.commit()
            return self.map_to_domain(orm_port)

    def batch_create_port(self, ports: list[Port], session: Session) -> list[Port]:
        orm_list = [PortRepository.map_to_sql(port) for port in ports]
        session.add_all(orm_list)
        return [PortRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_domain(orm_port: OrmPort) -> Port:
        return Port(
            id=orm_port.id,
            name=orm_port.name,
            locode=orm_port.locode,
            url=orm_port.url,
            country_iso3=orm_port.country_iso3,
            latitude=orm_port.latitude,
            longitude=orm_port.longitude,
            geometry_point=to_shape(orm_port.geometry_point),
            geometry_buffer=to_shape(orm_port.geometry_buffer)
            if orm_port.geometry_buffer is not None
            else None,
            has_excursion=orm_port.has_excursion,
            created_at=orm_port.created_at,
            updated_at=orm_port.updated_at,
        )

    @staticmethod
    def map_to_sql(port: Port) -> OrmPort:
        return OrmPort(
            name=port.name,
            locode=port.locode,
            url=port.url,
            country_iso3=port.country_iso3,
            latitude=port.latitude,
            longitude=port.longitude,
            geometry_point=from_shape(port.geometry_point),
            geometry_buffer=from_shape(port.geometry_buffer)
            if port.geometry_buffer is not None
            else None,
            has_excursion=port.has_excursion,
            created_at=port.created_at,
            updated_at=port.updated_at,
        )
