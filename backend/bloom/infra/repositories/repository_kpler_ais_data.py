from bloom.domain.kpler_ais_data import KplerAisData
import pandas as pd
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy.orm import Session


class KplerAisDataRepository:
   
    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def batch_create_ais_data(
            self, ais_list: list[KplerAisData], session: Session
    ) -> list[KplerAisData]:
        orm_list = [KplerAisDataRepository.map_to_orm(ais) for ais in ais_list]
        session.add_all(orm_list)
        return [KplerAisDataRepository.map_to_domain(orm) for orm in orm_list]
    
    @staticmethod
    def map_to_orm(data: KplerAisData) -> sql_model.KplerAisData:
        return sql_model.KplerAisData(**data.__dict__)

    @staticmethod
    def map_to_domain(orm_data: sql_model.KplerAisData) -> KplerAisData:
        return KplerAisData(
            id = orm_data.id,
            position_id = orm_data.position_id,
            vessel_uid = orm_data.vessel_uid,
            vessel_flag = orm_data.vessel_flag,
            vessel_name = orm_data.vessel_name,
            vessel_callsign = orm_data.vessel_callsign,
            vessel_mmsi = orm_data.vessel_mmsi,
            vessel_imo = orm_data.vessel_imo,
            vessel_marinetraffic_type = orm_data.vessel_marinetraffic_type,
            vessel_ais_type=orm_data.vessel_ais_type,
            vessel_width = orm_data.vessel_width,
            vessel_length = orm_data.vessel_length,
            vessel_grt = orm_data.vessel_grt,
            vessel_dwt= orm_data.vessel_dwt,
            static_timestamp = orm_data.static_timestamp,
            static_source= orm_data.static_source,
            static_message_type= orm_data.static_message_type,
            position_message_type= orm_data.position_message_type,
            position_source = orm_data.position_source,
            position_course = orm_data.position_course,
            position_heading = orm_data.position_heading,
            position_longitude = orm_data.position_longitude,
            position_latitude = orm_data.position_latitude,
            position_navigational_status = orm_data.position_navigational_status,
            position_rot = orm_data.position_rot,
            position_speed= orm_data.position_speed,
            position_timestamp = orm_data.position_timestamp,
            position_kpler_insert_timestamp = orm_data.position_kpler_insert_timestamp,
            voyage_destination = orm_data.voyage_destination,
            voyage_draught = orm_data.voyage_draught,
            voyage_eta = orm_data.voyage_eta,
            payload = orm_data.payload,
            created_at = orm_data.created_at
        )