from contextlib import AbstractContextManager

from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape

from bloom.domain.segment import Segment
from bloom.infra.database import sql_model


class SegmentRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    @staticmethod
    def map_to_domain(segment: sql_model.Segment) -> Segment:
        return Segment(
            id=segment.id,
            excursion_id=segment.id,
            timestamp_start=segment.timestamp_start,
            timestamp_end=segment.timestamp_end,
            segment_duration=segment.segment_duration,
            start_position=to_shape(segment.start_position),
            end_position=to_shape(segment.end_position),
            heading=segment.heading,
            distance=segment.distance,
            average_speed=segment.average_speed,
            speed_at_start=segment.speed_at_start,
            speed_at_and=segment.speed_at_end,
            heading_at_start=segment.speed_at_start,
            heading_at_and=segment.speed_at_end,
            type=segment.type,
            in_amp_zone=segment.in_amp_zone,
            in_territorial_waters=segment.in_territorial_waters,
            in_costal_waters=segment.in_costal_waters,
            last_vessel_sgement=segment.last_vessel_segment,
            created_at=segment.created_at,
            updated_at=segment.updated_at
        )

    @staticmethod
    def map_to_orm(segment: Segment) -> sql_model.Segment:
        return sql_model.Segment(
            id=segment.id,
            excursion_id=segment.id,
            timestamp_start=segment.timestamp_start,
            timestamp_end=segment.timestamp_end,
            segment_duration=segment.segment_duration,
            start_position=from_shape(segment.start_position),
            end_position=from_shape(segment.end_position),
            heading=segment.heading,
            distance=segment.distance,
            average_speed=segment.average_speed,
            speed_at_start=segment.speed_at_start,
            speed_at_and=segment.speed_at_end,
            heading_at_start=segment.speed_at_start,
            heading_at_and=segment.speed_at_end,
            type=segment.type,
            in_amp_zone=segment.in_amp_zone,
            in_territorial_waters=segment.in_territorial_waters,
            in_costal_waters=segment.in_costal_waters,
            last_vessel_sgement=segment.last_vessel_segment,
            created_at=segment.created_at,
            updated_at=segment.updated_at
        )
