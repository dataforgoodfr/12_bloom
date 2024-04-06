from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy import select
from dependency_injector.providers import Callable
from bloom.domain.excursion import Excursion
from typing import Union
from bloom.infra.database import sql_model
from geoalchemy2.shape import from_shape, to_shape


class ExcursionRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_vessel_current_excursion(self, session: Session, vessel_id: int) -> Union[Excursion | None]:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        sql = select(sql_model.Excursion).where(sql_model.Excursion.vessel_id == vessel_id).where(
            sql_model.Excursion.arrival_at.isnot(None))
        e = session.execute(sql).scalar()
        if not e:
            return None
        return ExcursionRepository.map_to_domain(e)

    @staticmethod
    def map_to_domain(excursion: sql_model.Excursion) -> Excursion:
        return Excursion(
            id=excursion.id,
            vessel_id=excursion.vessel_id,
            departure_port_id=excursion.departure_port_id,
            departure_at=excursion.departure_at,
            departure_position=to_shape(excursion.departure_position),
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position=to_shape(excursion.arrival_position),
            excursion_duration=excursion.excursion_duration,
            total_time_at_sea=excursion.total_time_at_sea,
            total_time_in_amp=excursion.total_time_in_amp,
            total_time_in_territorial_waters=excursion.total_time_fishing_in_territorial_waters,
            total_time_in_costal_waters=excursion.total_time_fishing_in_costal_waters,
            total_time_fishing=excursion.total_time_fishing,
            total_time_fishing_in_amp=excursion.total_time_fishing_in_amp,
            total_time_fishing_in_territorial_waters=excursion.total_time_fishing_in_territorial_waters,
            total_time_fishing_in_costal_waters=excursion.total_time_fishing_in_costal_waters,
            total_time_extincting_amp=excursion.total_time_extincting_amp,
            created_at=excursion.created_at,
            updated_at=excursion.updated_at
        )

    @staticmethod
    def map_to_orm(excursion: Excursion) -> sql_model.Excursion:
        return sql_model.Excursion(
            id=excursion.id,
            vessel_id=excursion.vessel_id,
            departure_port_id=excursion.departure_port_id,
            departure_at=excursion.departure_at,
            departure_position=from_shape(excursion.departure_position),
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position=from_shape(excursion.arrival_position),
            excursion_duration=excursion.excursion_duration,
            total_time_at_sea=excursion.total_time_at_sea,
            total_time_in_amp=excursion.total_time_in_amp,
            total_time_in_territorial_waters=excursion.total_time_fishing_in_territorial_waters,
            total_time_in_costal_waters=excursion.total_time_fishing_in_costal_waters,
            total_time_fishing=excursion.total_time_fishing,
            total_time_fishing_in_amp=excursion.total_time_fishing_in_amp,
            total_time_fishing_in_territorial_waters=excursion.total_time_fishing_in_territorial_waters,
            total_time_fishing_in_costal_waters=excursion.total_time_fishing_in_costal_waters,
            total_time_extincting_amp=excursion.total_time_extincting_amp,
            created_at=excursion.created_at,
            updated_at=excursion.updated_at
        )
