from contextlib import AbstractContextManager
from datetime import datetime

import pandas as pd
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from shapely import wkb
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_Within
from bloom.infra.repositories.repository_zone import ZoneRepository

from bloom.domain.segment import Segment
from bloom.domain.zone import Zone
from bloom.infra.database import sql_model


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
            sql_model.Segment.end_position,
            sql_model.Segment.timestamp_end
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
        df = pd.DataFrame(q, columns=["vessel_id", "excursion_id", "end_position", "timestamp_end"])
        df["end_position"] = df["end_position"].astype(str).apply(wkb.loads)
        return df

    def batch_create_segment(
            self, session: Session, segments: list[Segment]
    ) -> list[Segment]:
        orm_list = [SegmentRepository.map_to_orm(segment) for segment in segments]
        session.add_all(orm_list)
        return [SegmentRepository.map_to_domain(orm) for orm in orm_list]

    def get_segments_created_updated_after(self, session: Session, created_updated_after: datetime) -> list[Segment]:
        stmt = select(sql_model.Segment).where(
            or_(and_(sql_model.Segment.updated_at == None, sql_model.Segment.created_at > created_updated_after),
                sql_model.Segment.updated_at > created_updated_after)
        )
        result = session.execute(stmt).scalars()
        return [SegmentRepository.map_to_domain(orm) for orm in result]

    def find_segments_in_zones_created_updated_after(self, session: Session, created_updated_after: datetime) -> dict[
        Segment, list[Zone]]:
        stmt = select(sql_model.Segment, sql_model.Zone).where(
            or_(and_(sql_model.Segment.updated_at == None, sql_model.Segment.created_at > created_updated_after),
                sql_model.Segment.updated_at > created_updated_after)
        ).join(sql_model.Zone, and_(ST_Within(sql_model.Segment.start_position, sql_model.Zone.geometry),
                                    ST_Within(sql_model.Segment.end_position, sql_model.Zone.geometry)))
        result = session.execute(stmt)
        dict = {}
        for (segment, zone) in result:
            segment = SegmentRepository.map_to_domain(segment)
            zone = ZoneRepository.map_to_domain(zone)
            dict.setdefault(segment, []).append(zone)
        return dict

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
            course=segment.course,
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
            course=segment.course,
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
