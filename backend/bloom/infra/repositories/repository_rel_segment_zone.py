from sqlalchemy.orm import Session

from bloom.domain.rel_segment_zone import RelSegmentZone
from bloom.infra.database import sql_model


class RelSegmentZoneRepository:

    @staticmethod
    def batch_create_rel_segment_zone(session: Session, rels: list[RelSegmentZone]) -> list[RelSegmentZone]:
        orm_list = [RelSegmentZoneRepository.map_to_orm(rel) for rel in rels]
        session.add_all(orm_list)
        session.flush()
        return [RelSegmentZoneRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_orm(domain: RelSegmentZone) -> sql_model.RelSegmentZone:
        return sql_model.RelSegmentZone(
            segment_id=domain.segment_id,
            zone_id=domain.zone_id,
            created_at=domain.created_at,
        )

    @staticmethod
    def map_to_domain(orm: sql_model.RelSegmentZone) -> RelSegmentZone:
        return RelSegmentZone(
            segment_id=orm.segment_id,
            zone_id=orm.zone_id,
            created_at=orm.created_at,
        )
