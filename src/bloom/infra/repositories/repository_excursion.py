import pandas as pd
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from sqlalchemy import select
from dependency_injector.providers import Callable
from bloom.domain.excursion import Excursion
from typing import Union
from bloom.infra.database import sql_model


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

    def get_current_excursions(self, session: Session) -> pd.DataFrame:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        sql = select(
            sql_model.Excursion.id,
            sql_model.Excursion.vessel_id,
            sql_model.Excursion.arrival_at
        ).where(sql_model.Excursion.arrival_at == None)
        excursions = session.execute(sql)
        if not excursions:
            return None
        return pd.DataFrame(excursions, columns=["excursion_id", "vessel_id", "arrival_at"])
    
    def batch_create_excursion(self, session: Session, ports: list[Excursion]) -> list[Excursion]:
        orm_list = [ExcursionRepository.map_to_sql(port) for port in ports]
        session.add_all(orm_list)
        return [ExcursionRepository.map_to_domain(orm) for orm in orm_list]

    @staticmethod
    def map_to_sql(excursion: Excursion) -> sql_model.Excursion:
        return sql_model.Excursion(
            id=excursion.id,
            vessel_id=excursion.vessel_id,
            departure_port_id=excursion.departure_port_id,
            departure_at=excursion.departure_at,
            departure_position_id=excursion.departure_position_id,
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position_id=excursion.arrival_position_id,
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
    def map_to_domain(excursion: sql_model.Excursion) -> Excursion:
        return Excursion(
            id=excursion.id,
            vessel_id=excursion.vessel_id,
            departure_port_id=excursion.departure_port_id,
            departure_at=excursion.departure_at,
            departure_position_id=excursion.departure_position_id,
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position_id=excursion.arrival_position_id,
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
