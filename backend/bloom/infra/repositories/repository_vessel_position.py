from datetime import datetime
from typing import Any, List, Union

import pandas as pd
from bloom.infra.repositories import AbstractRepository
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from bloom.config import settings
from bloom.domain.vessel_position import VesselPosition
from bloom.infra.database import sql_model

from bloom.logger import logger


class VesselPositionRepository(AbstractRepository):
    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def create_vessel_position(self, session: Session, position: VesselPosition) -> VesselPosition:
        orm_position = VesselPositionRepository.map_to_sql(position)
        session.add(orm_position)
        return VesselPositionRepository.map_to_domain(orm_position)

    def batch_create_vessel_position(self, session: Session, vessel_positions: list[VesselPosition]) -> list[
        VesselPosition]:
        orm_list = [VesselPositionRepository.map_to_sql(vessel_position) for vessel_position in vessel_positions]
        session.add_all(orm_list)
        return [VesselPositionRepository.map_to_domain(orm) for orm in orm_list]

    def get_all_vessel_last_positions(self, session: Session) -> List[VesselPosition]:
        
        stmt=select(sql_model.VesselPosition)\
                        .order_by(sql_model.VesselPosition.timestamp.desc())\
                        .group_by(sql_model.VesselPosition.vessel_id)
        result = session.execute(stmt).scalars()
        #logger.info(type(result))
        if result is not None :
            return [VesselPositionRepository.map_to_domain(record) for record in result]
        else:
            return []

    def get_vessel_positions(self, session: Session, vessel_id:int,
                             start:datetime=datetime.now(),
                             end:datetime=None) -> List[VesselPosition]:
        
        stmt=select(sql_model.VesselPosition).filter_by(vessel_id=vessel_id).order_by(sql_model.VesselPosition.timestamp.desc())
        result = session.execute(stmt).scalars()
        #logger.info(type(result))
        if result is not None :
            return [VesselPositionRepository.map_to_domain(record) for record in result]
        else:
            return []

    def get_positions_with_vessel_created_updated_after(self, session: Session,
                                                        created_updated_after: datetime) -> pd.DataFrame:
        stmt = select(sql_model.VesselPosition.id, sql_model.VesselPosition.timestamp,
                      sql_model.VesselPosition.accuracy, sql_model.VesselPosition.collection_type,
                      sql_model.VesselPosition.course, sql_model.VesselPosition.heading,
                      sql_model.VesselPosition.position, sql_model.VesselPosition.longitude,
                      sql_model.VesselPosition.latitude, sql_model.VesselPosition.rot,
                      sql_model.VesselPosition.speed, sql_model.VesselPosition.created_at,
                      sql_model.Vessel.id, sql_model.Vessel.mmsi).where(
            sql_model.VesselPosition.created_at > created_updated_after
        ).join(sql_model.Vessel, sql_model.VesselPosition.vessel_id == sql_model.Vessel.id).order_by(
            sql_model.VesselPosition.created_at.asc())

        result = session.execute(stmt)
        df = pd.DataFrame(result,
                          columns=["id", "timestamp", "accuracy", "collection_type", "course", "heading", "position",
                                   "longitude", "latitude", "rot", "speed", "created_at", "vessel_id", "mmsi"])
        df["position"] = df["position"].apply(to_shape)
        return df

    @staticmethod
    def map_to_sql(position: VesselPosition) -> sql_model.VesselPosition:
        return sql_model.VesselPosition(
            id=position.id,
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
            id=position.id,
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
