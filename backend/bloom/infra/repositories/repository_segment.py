import pandas as pd
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy import select
from dependency_injector.providers import Callable
from bloom.domain.excursion import Excursion
from typing import Union
from bloom.infra.database import sql_model
from bloom.domain.segment import Segment
from geoalchemy2.shape import from_shape, to_shape
from shapely import wkb

from bloom.logger import logger


class SegmentRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_segments_by_excursions(self, session: Session, id: int) -> pd.DataFrame :
        stmt= select(
                    sql_model.Segment.segment_duration,
                    sql_model.Segment.in_amp_zone,
                      sql_model.Segment.in_territorial_waters,
                       sql_model.Segment.in_costal_waters
        ).where(sql_model.Segment.excursion_id== id)
        q = session.execute(stmt)
        if not q:
            return None
        df = pd.DataFrame(q, columns=["segment_duration", "in_amp_zone", "in_territorial_waters", "in_costal_waters"])
        return df

    def get_last_vessel_id_segments(self, session: Session) -> pd.DataFrame:
        stmt = select(
            sql_model.Vessel.id,
            sql_model.Segment.excursion_id,
            sql_model.Segment.end_position,
            sql_model.Segment.timestamp_end,
            sql_model.Segment.heading_at_end,
            sql_model.Segment.speed_at_end,
            sql_model.Excursion.arrival_port_id,
            sql_model.Vessel.mmsi
        ).join(
            sql_model.Excursion,
            sql_model.Segment.excursion_id == sql_model.Excursion.id

        ).join(
            sql_model.Vessel,
            sql_model.Excursion.vessel_id == sql_model.Vessel.id

        ).filter(
            sql_model.Segment.last_vessel_segment == True
        )
        q = session.execute(stmt)
        if not q:
            return None
        df = pd.DataFrame(q, columns=["vessel_id", "excursion_id", "end_position", "timestamp_end",'heading_at_end','speed_at_end','arrival_port_id','mmsi'])
        df["end_position"] = df["end_position"].astype(str).apply(wkb.loads)
        return df

    def batch_create_segment(
            self, session: Session, segments: list[Segment]
    ) -> list[Segment]:
        orm_list = [SegmentRepository.map_to_orm(segment) for segment in segments]
        session.add_all(orm_list)
        return [SegmentRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_domain(segment: sql_model.Segment) -> Segment:
        return Segment(
            id=segment.id,
            excursion_id=segment.excursion_id,
            timestamp_start=segment.timestamp_start,
            timestamp_end=segment.timestamp_end,
            segment_duration=segment.segment_duration,
            start_position=to_shape(segment.start_position),
            end_position=to_shape(segment.end_position),
            distance=segment.distance,
            average_speed=segment.average_speed,
            speed_at_start=segment.speed_at_start,
            speed_at_end=segment.speed_at_end,
            heading_at_start=segment.speed_at_start,
            heading_at_end=segment.speed_at_end,
            type=segment.type,
            in_amp_zone=segment.in_amp_zone,
            in_territorial_waters=segment.in_territorial_waters,
            in_costal_waters=segment.in_costal_waters,
            last_vessel_segment=segment.last_vessel_segment,
            created_at=segment.created_at,
            updated_at=segment.updated_at
        )

    @staticmethod
    def map_to_orm(segment: Segment) -> sql_model.Segment:
        return sql_model.Segment(
            id=segment.id,
            excursion_id=segment.excursion_id,
            timestamp_start=segment.timestamp_start,
            timestamp_end=segment.timestamp_end,
            segment_duration=segment.segment_duration,
            start_position=from_shape(segment.start_position),
            end_position=from_shape(segment.end_position),
            distance=segment.distance,
            average_speed=segment.average_speed,
            speed_at_start=segment.speed_at_start,
            speed_at_end=segment.speed_at_end,
            heading_at_start=segment.speed_at_start,
            heading_at_end=segment.speed_at_end,
            type=segment.type,
            in_amp_zone=segment.in_amp_zone,
            in_territorial_waters=segment.in_territorial_waters,
            in_costal_waters=segment.in_costal_waters,
            last_vessel_segment=segment.last_vessel_segment,
            created_at=segment.created_at,
            updated_at=segment.updated_at
        )
