from geoalchemy2.shape import from_shape, to_shape
from bloom.config import settings
from bloom.infra.database import sql_model
from bloom.domain.vessel_position import VesselPosition
from sqlalchemy.orm import Session
from dependency_injector.providers import Callable


class VesselPositionRepository:
    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def create_vessel_position(self, session: Session, position: VesselPosition) -> VesselPosition:
        orm_position = VesselPositionRepository.map_to_sql(position)
        session.add(orm_position)
        return VesselPositionRepository.map_to_domain(orm_position)

    @staticmethod
    def map_to_sql(position: VesselPosition) -> sql_model.VesselPosition:
        return sql_model.VesselPosition(
            timestamp=position.timestamp,
            accuracy=position.accuracy,
            collection_type=position.collection_type,
            course=position.course,
            heading=position.heading,
            position=from_shape(position.position, srid=settings.srid),
            latitude=position.latitude,
            longitude=position.longitude,
            maneuver=position.maneuver,
            navigational_status=position.navigational_status,
            rot=position.rot,
            speed=position.speed,
            vessel_id=position.vessel_id
        )

    @staticmethod
    def map_to_domain(position: sql_model.VesselPosition) -> VesselPosition:
        return VesselPosition(
            timestamp=position.timestamp,
            accuracy=position.accuracy,
            collection_type=position.collection_type,
            course=position.course,
            heading=position.heading,
            position=to_shape(position.position),
            latitude=position.latitude,
            longitude=position.longitude,
            maneuver=position.maneuver,
            navigational_Status=position.navigational_status,
            rot=position.rot,
            speed=position.speed,
            vessel_id=position.vessel_id
        )
