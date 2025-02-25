from dependency_injector.providers import Callable
from bloom.domain.position_update import PositionUpdate
from bloom.infra.database import sql_model
from sqlalchemy.orm import Session
from sqlalchemy import select


class PositionUpdateRepository:

    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    @staticmethod
    def find_record_by_vessel_id(
        session: Session, vessel_id: int
    ) -> PositionUpdate | None:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        stmt = select(sql_model.PositionUpdate).where(
            (sql_model.PositionUpdate.vessel_id == vessel_id)
        )
        result = session.execute(stmt).scalar_one_or_none()
        if not result:
            return None
        return PositionUpdateRepository.map_to_domain(result)

    def batch_update_position_timestamp_update(
        self, session: Session, position_updates: list[PositionUpdate]
    ) -> list[PositionUpdate]:
        updated_position_timestamp_updates = []
        for entity in position_updates:
            orm = PositionUpdateRepository.map_to_sql(entity)
            session.merge(orm)
            session.flush()
            updated_position_timestamp_updates.append(
                PositionUpdateRepository.map_to_domain(orm)
            )
        return updated_position_timestamp_updates

    @staticmethod
    def map_to_sql(position_update: PositionUpdate) -> sql_model.PositionUpdate:
        return sql_model.PositionUpdate(
            id=position_update.id,
            vessel_id=position_update.vessel_id,
            point_in_time=position_update.point_in_time,
            created_at=position_update.created_at,
            updated_at=position_update.updated_at,
        )

    @staticmethod
    def map_to_domain(position_update: sql_model.PositionUpdate) -> PositionUpdate:
        return PositionUpdate(
            id=position_update.id,
            vessel_id=position_update.vessel_id,
            point_in_time=position_update.point_in_time,
            created_at=position_update.created_at,
            updated_at=position_update.updated_at,
        )
