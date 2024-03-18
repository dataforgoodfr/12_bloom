from bloom.domain.spire_ais_data import SpireAisData
from bloom.infra.database.sql_model import SpireAisData as OrmSpireAisData
from dependency_injector.providers import Callable


class SpireAisDataRepository:
    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def create_ais_data(self, ais_data: SpireAisData) -> OrmSpireAisData:
        with self.session_factory() as session:
            sql_ais_data = SpireAisDataRepository.map_to_orm(ais_data)
            session.add(sql_ais_data)
            session.commit()
            return SpireAisDataRepository.map_to_domain(sql_ais_data)

    def batch_create_ais_data(self, ais_list: list[SpireAisData]) -> list[SpireAisData]:
        with self.session_factory() as session:
            orm_list = [SpireAisDataRepository.map_to_orm(ais) for ais in ais_list]
            session.add_all(orm_list)
            session.commit()
            return [SpireAisDataRepository.map_to_domain(orm) for orm in orm_list]

    def map_to_orm(data: SpireAisData) -> OrmSpireAisData:
        return OrmSpireAisData(**data.__dict__)

    def map_to_domain(orm_data: OrmSpireAisData) -> SpireAisData:
        return SpireAisData(
            id=orm_data.id,
            spire_update_statement=orm_data.spire_update_statement,
            vessel_ais_class=orm_data.vessel_ais_class,
            vessel_flag=orm_data.vessel_flag,
            vessel_name=orm_data.vessel_name,
            vessel_callsign=orm_data.vessel_callsign,
            vessel_timestamp=orm_data.vessel_timestamp,
            vessel_update_timestamp=orm_data.vessel_update_timestamp,
            vessel_ship_type=orm_data.vessel_ship_type,
            vessel_sub_ship_type=orm_data.vessel_sub_ship_type,
            vessel_mmsi=orm_data.vessel_mmsi,
            vessel_imo=orm_data.vessel_imo,
            vessel_width=orm_data.vessel_width,
            vessel_length=orm_data.vessel_length,
            position_accuracy=orm_data.position_accuracy,
            position_collection_type=orm_data.position_collection_type,
            position_course=orm_data.position_course,
            position_heading=orm_data.position_heading,
            position_latitude=orm_data.position_latitude,
            position_longitude=orm_data.position_longitude,
            position_maneuver=orm_data.position_maneuver,
            position_navigational_status=orm_data.position_navigational_status,
            position_rot=orm_data.position_rot,
            position_speed=orm_data.position_speed,
            position_timestamp=orm_data.position_timestamp,
            position_update_timestamp=orm_data.position_update_timestamp,
            voyage_destination=orm_data.voyage_destination,
            voyage_draught=orm_data.voyage_draught,
            voyage_eta=orm_data.voyage_eta,
            voyage_timestamp=orm_data.voyage_timestamp,
            voyage_update_timestamp=orm_data.voyage_update_timestamp,
        )
