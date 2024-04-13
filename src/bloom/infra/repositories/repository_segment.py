import pandas as pd
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy import select
from dependency_injector.providers import Callable
from bloom.domain.excursion import Excursion
from typing import Union
from bloom.infra.database import sql_model
from bloom.domain.segment import Segment

from bloom.logger import logger


class SegmentRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_last_vessel_id_segments(self, session: Session) -> pd.DataFrame:
        stmt = select(
            sql_model.Vessel.id,
            sql_model.Segment.excursion_id,
            sql_model.VesselPosition.longitude,
            sql_model.VesselPosition.latitude,
            sql_model.Segment.timestamp_end
        ).join(
            sql_model.Excursion,
            sql_model.Segment.excursion_id == sql_model.Excursion.id
            
        ).join(
            sql_model.Vessel,
            sql_model.Excursion.vessel_id == sql_model.Vessel.id
            
        ).join(
            sql_model.VesselPosition,
            sql_model.Segment.end_position_id == sql_model.VesselPosition.id
        ).filter(
            sql_model.Segment.last_vessel_segment == True
        )
        q = session.execute(stmt)
        if not q:
            return None
        return pd.DataFrame(q, columns=["vessel_id", "excursion_id", "longitude", "latitude", "timestamp_end"])
    
    def batch_create_segment(
            self, session: Session, segments: list[Segment]
    ) -> list[Segment]:
        orm_list = [SegmentRepository.map_to_orm(segment) for segment in segments]
        session.add_all(orm_list)
        return [SegmentRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_orm(segment: Segment) -> sql_model.Segment:
        return sql_model.Segment(
            id=segment.id,
            excursion_id=segment.excursion_id,
            timestamp_start=segment.timestamp_start,
            timestamp_end=segment.timestamp_end,
            segment_duration=segment.segment_duration,
            start_position_id=segment.start_position_id,
            end_position_id=segment.end_position_id,
            heading=segment.heading,
            distance=segment.distance,
            average_speed=segment.average_speed,
            # speed_at_start=segment.#,
            # speed_at_end=segment.#,
            type=segment.type,
            in_amp_zone=segment.in_amp_zone,
            in_territorial_waters=segment.in_territorial_waters,
            in_costal_waters=segment.in_costal_waters,
            last_vessel_segment=segment.last_vessel_segment,
            created_at=segment.created_at,
            updated_at=segment.updated_at,
        )

    @staticmethod
    def map_to_domain(orm_data: sql_model.Segment) -> Segment:
        return Segment(
            id=orm_data.id, 
            excursion_id=orm_data.excursion_id, 
            timestamp_start=orm_data.timestamp_start, 
            timestamp_end=orm_data.timestamp_end, 
            segment_duration=orm_data.segment_duration, 
            start_position_id=orm_data.start_position_id, 
            end_position_id=orm_data.end_position_id, 
            heading=orm_data.heading, 
            distance=orm_data.distance, 
            average_speed=orm_data.average_speed, 
            type=orm_data.type, 
            in_amp_zone=orm_data.in_amp_zone, 
            in_territorial_waters=orm_data.in_territorial_waters, 
            in_costal_waters=orm_data.in_costal_waters, 
            last_vessel_segment=orm_data.last_vessel_segment, 
            created_at=orm_data.created_at, 
            updated_at=orm_data.updated_at, 
        )