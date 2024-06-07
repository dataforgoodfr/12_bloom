from contextlib import AbstractContextManager
from typing import Any, List, Union

import pandas as pd
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.orm import Session

from bloom.domain.excursion import Excursion
from bloom.infra.database import sql_model


class ExcursionRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_param_from_last_excursion(self, session: Session, vessel_id: int) -> Union[dict, None]:
        """Recherche l'excursion la plus récente d'un bateau et retourne l'arrival_port_id et la position d'arrivée."""
        sql = select(
            sql_model.Excursion.arrival_port_id,
            sql_model.Excursion.arrival_position
        ).where(
            sql_model.Excursion.vessel_id == vessel_id
        ).order_by(
            desc(sql_model.Excursion.departure_at)
        ).limit(1)
        result = session.execute(sql).one_or_none()
        if not result:
            return None
        return {"arrival_port_id": result.arrival_port_id, "arrival_position": result.arrival_position}

    def get_excursions_by_vessel_id(self, session: Session, vessel_id: int) -> List[Excursion]:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        stmt = select(sql_model.Excursion).where(sql_model.Excursion.vessel_id == vessel_id)
        result = session.execute(stmt).all()
        print(result)
        if not result:
            return []
        return [ ExcursionRepository.map_to_domain(r[0]) for r in result]
    
    def get_vessel_excursion_by_id(self, session: Session, vessel_id: int, excursion_id:int) -> Union[Excursion,None]:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        stmt = select(sql_model.Excursion).where( (sql_model.Excursion.vessel_id == vessel_id )
                                                 & (sql_model.Excursion.id == excursion_id ))
        result = session.execute(stmt).fetchone()
        if not result :
            return None
        return ExcursionRepository.map_to_domain(result[0])



    def get_excursion_by_id(self, session: Session, id: int) -> Union[Excursion, None]:
        """Recheche l'excursion en cours d'un bateau, c'est-à-dire l'excursion qui n'a pas de date d'arrivée"""
        sql = select(sql_model.Excursion).where(sql_model.Excursion.id == id)
        e = session.execute(sql).scalar()
        if not e:
            return None
        return ExcursionRepository.map_to_domain(e)

    def get_vessel_current_excursion(self, session: Session, vessel_id: int) -> Union[Excursion, None]:
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

    def create_excursion(self, session: Session, excursion: Excursion) -> Excursion:
        orm_excursion = ExcursionRepository.map_to_sql(excursion)
        session.add(orm_excursion)
        session.flush()
        return ExcursionRepository.map_to_domain(orm_excursion)

    def batch_create_excursion(self, session: Session, excursions: list[Excursion]) -> list[Excursion]:
        orm_list = [ExcursionRepository.map_to_sql(excursion) for excursion in excursions]
        session.add_all(orm_list)
        session.flush()
        return [ExcursionRepository.map_to_domain(orm) for orm in orm_list]

    def update_excursion(self, session: Session, excursion: Excursion) -> Excursion:
        orm_excursion = ExcursionRepository.map_to_sql(excursion)
        res = session.merge(orm_excursion)
        session.flush()
        return ExcursionRepository.map_to_domain(res)

    def batch_update_excursion(self, session: Session, excursions: list[Excursion]) -> list[Excursion]:
        updated_excursion = []
        for excursion in excursions:
            orm = ExcursionRepository.map_to_sql(excursion)
            session.merge(orm)
            session.flush()
            updated_excursion.append(ExcursionRepository.map_to_domain(orm))
        return updated_excursion

    def get_excursion_by_id(self, session: Session, excursion_id: int) -> Excursion:
        entity = session.get(sql_model.Excursion, excursion_id)  # .scalar()
        if entity is not None:
            return ExcursionRepository.map_to_domain(entity)
        else:
            return None

    @staticmethod
    def map_to_sql(excursion: Excursion) -> sql_model.Excursion:
        return sql_model.Excursion(
            id=excursion.id,
            vessel_id=excursion.vessel_id,
            departure_port_id=excursion.departure_port_id,
            departure_at=excursion.departure_at,
            departure_position=from_shape(
                excursion.departure_position) if excursion.departure_position is not None else None,
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position=from_shape(excursion.arrival_position) if excursion.arrival_position else None,
            excursion_duration=excursion.excursion_duration,
            total_time_at_sea=excursion.total_time_at_sea,
            total_time_in_amp=excursion.total_time_in_amp,
            total_time_in_territorial_waters=excursion.total_time_in_territorial_waters,
            total_time_in_costal_waters=excursion.total_time_in_costal_waters,
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
            departure_position=to_shape(excursion.departure_position) if excursion.departure_position else None,
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position=to_shape(excursion.arrival_position) if excursion.arrival_position else None,
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
            departure_position=from_shape(
                excursion.departure_position) if excursion.departure_position is not None else None,
            arrival_port_id=excursion.arrival_port_id,
            arrival_at=excursion.arrival_at,
            arrival_position=from_shape(excursion.arrival_position) if excursion.arrival_position is not None else None,
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
