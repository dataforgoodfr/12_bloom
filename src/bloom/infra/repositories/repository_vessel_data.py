from bloom.domain.vessel_data import VesselData
from bloom.infra.database import sql_model
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Union


class VesselDataRepository:

    @staticmethod
    def create_vessel_data(session: Session, data: VesselData) -> VesselData:
        orm_data = VesselDataRepository.map_to_sql(data)
        session.add(orm_data)
        return VesselDataRepository.map_to_domain(orm_data)

    @staticmethod
    def get_last_vessel_data(session: Session, vessel_id: int) -> Union[VesselData, None]:
        stmt = select(sql_model.VesselData).distinct(sql_model.VesselData.vessel_id).order_by(
            sql_model.VesselData.vessel_id, sql_model.VesselData.timestamp.desc()).where(
            sql_model.VesselData.vessel_id == vessel_id)
        e = session.execute(stmt).scalar()
        if e:
            return VesselDataRepository.map_to_domain(e)
        else:
            return None

    @staticmethod
    def map_to_sql(data: VesselData) -> sql_model.VesselData:
        return sql_model.VesselData(
            id=data.id,
            timestamp=data.timestamp,
            ais_class=data.ais_class,
            flag=data.flag,
            name=data.name,
            callsign=data.name,
            ship_type=data.ship_type,
            sub_ship_type=data.sub_ship_type,
            mmsi=data.mmsi,
            imo=data.imo,
            width=data.width,
            length=data.length,
            vessel_id=data.vessel_id,
            created_at=data.created_at
        )

    @staticmethod
    def map_to_domain(data: sql_model.VesselData) -> VesselData:
        return VesselData(
            id=data.id,
            timestamp=data.timestamp,
            ais_class=data.ais_class,
            flag=data.flag,
            name=data.name,
            callsign=data.name,
            ship_type=data.ship_type,
            sub_ship_type=data.sub_ship_type,
            mmsi=data.mmsi,
            imo=data.imo,
            width=data.width,
            length=data.length,
            vessel_id=data.vessel_id,
            created_at=data.created_at
        )
