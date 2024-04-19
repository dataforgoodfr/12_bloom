from bloom.domain.vessel_voyage import VesselVoyage
from bloom.infra.database import sql_model
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Union


class VesselVoyageRepository:

    @staticmethod
    def create_vessel_voyage(session: Session, data: VesselVoyage) -> VesselVoyage:
        orm_data = VesselVoyageRepository.map_to_sql(data)
        session.add(orm_data)
        return VesselVoyageRepository.map_to_domain(orm_data)

    @staticmethod
    def get_last_vessel_voyage(session: Session, vessel_id: int) -> Union[VesselVoyage, None]:
        stmt = select(sql_model.VesselVoyage).distinct(sql_model.VesselVoyage.vessel_id).order_by(
            sql_model.VesselVoyage.vessel_id, sql_model.VesselVoyage.timestamp.desc()).where(
            sql_model.VesselVoyage.vessel_id == vessel_id)
        e = session.execute(stmt).scalar()
        if e:
            return VesselVoyageRepository.map_to_domain(e)
        else:
            return None

    @staticmethod
    def map_to_sql(data: VesselVoyage) -> sql_model.VesselVoyage:
        return sql_model.VesselVoyage(
            id=data.id,
            timestamp=data.timestamp,
            destination=data.destination,
            draught=data.draught,
            eta=data.eta,
            vessel_id=data.vessel_id,
            created_at=data.created_at,
        )

    @staticmethod
    def map_to_domain(data: sql_model.VesselVoyage) -> VesselVoyage:
        return VesselVoyage(
            id=data.id,
            timestamp=data.timestamp,
            destination=data.destination,
            draught=data.draught,
            eta=data.eta,
            vessel_id=data.vessel_id,
            created_at=data.created_at,
        )
