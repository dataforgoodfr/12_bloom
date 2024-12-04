import pandas as pd
from bloom.domain.spire_ais_data import SpireAisData
from bloom.infra.database import sql_model
from dependency_injector.providers import Callable
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from datetime import datetime
from bloom.logger import logger


class SpireAisDataRepository:
    ORDER_BY_VESSEL = "vessel"
    ORDER_BY_POSITION = "position"
    ORDER_BY_VOYAGE = "VOYAGE"

    def __init__(self, session_factory: Callable) -> None:
        self.session_factory = session_factory

    def create_ais_data(
            self, ais_data: SpireAisData, session: Session
    ) -> sql_model.SpireAisData:
        sql_ais_data = SpireAisDataRepository.map_to_orm(ais_data)
        session.add(sql_ais_data)
        return SpireAisDataRepository.map_to_domain(sql_ais_data)

    def batch_create_ais_data(
            self, ais_list: list[SpireAisData], session: Session
    ) -> list[SpireAisData]:
        orm_list = [SpireAisDataRepository.map_to_orm(ais) for ais in ais_list]
        session.add_all(orm_list)
        return [SpireAisDataRepository.map_to_domain(orm) for orm in orm_list]

    def get_all_data_after_date(
            self, session: Session, created_updated_after: datetime
    ) -> pd.DataFrame:
        stmt = select(
            sql_model.SpireAisData.id,
            sql_model.SpireAisData.spire_update_statement,
            sql_model.SpireAisData.vessel_mmsi,
            sql_model.Vessel.id,
            sql_model.SpireAisData.position_accuracy,
            sql_model.SpireAisData.position_collection_type,
            sql_model.SpireAisData.position_course,
            sql_model.SpireAisData.position_heading,
            sql_model.SpireAisData.position_latitude,
            sql_model.SpireAisData.position_longitude,
            sql_model.SpireAisData.position_maneuver,
            sql_model.SpireAisData.position_navigational_status,
            sql_model.SpireAisData.position_rot,
            sql_model.SpireAisData.position_speed,
            sql_model.SpireAisData.position_timestamp,
            sql_model.SpireAisData.position_update_timestamp,
            sql_model.SpireAisData.created_at,
        ).join(
            sql_model.Vessel,
            sql_model.Vessel.mmsi == sql_model.SpireAisData.vessel_mmsi
        ).where(
            and_(
                sql_model.Vessel.tracking_activated == True,
                sql_model.SpireAisData.created_at > created_updated_after
            )
        )
        result = session.execute(stmt)
        return pd.DataFrame(result, columns=[
            "id",
            "spire_update_statement",
            "vessel_mmsi",
            "vessel_id",
            "position_accuracy",
            "position_collection_type",
            "position_course",
            "position_heading",
            "position_latitude",
            "position_longitude",
            "position_maneuver",
            "position_navigational_status",
            "position_rot",
            "position_speed",
            "position_timestamp",
            "position_update_timestamp",
            "created_at"
        ],
                            )

    def get_all_data_between_date(
            self, session: Session, created_updated_after: datetime, created_updated_before: datetime
    ) -> pd.DataFrame:
        stmt = (
            select(
                sql_model.SpireAisData.id,
                sql_model.SpireAisData.spire_update_statement,
                sql_model.SpireAisData.vessel_mmsi,
                sql_model.SpireAisData.vessel_name,
                sql_model.SpireAisData.vessel_imo,
                sql_model.SpireAisData.vessel_callsign,
                sql_model.Vessel.id,
                sql_model.SpireAisData.position_accuracy,
                sql_model.SpireAisData.position_collection_type,
                sql_model.SpireAisData.position_course,
                sql_model.SpireAisData.position_heading,
                sql_model.SpireAisData.position_latitude,
                sql_model.SpireAisData.position_longitude,
                sql_model.SpireAisData.position_maneuver,
                sql_model.SpireAisData.position_navigational_status,
                sql_model.SpireAisData.position_rot,
                sql_model.SpireAisData.position_speed,
                sql_model.SpireAisData.position_timestamp,
                sql_model.SpireAisData.position_update_timestamp,
                sql_model.SpireAisData.created_at,
            )
            .join(
                sql_model.Vessel,
                sql_model.Vessel.mmsi == sql_model.SpireAisData.vessel_mmsi,
            )
            .where(
                and_(
                    sql_model.Vessel.tracking_activated == True,
                    sql_model.SpireAisData.created_at > created_updated_after,
                    sql_model.SpireAisData.created_at <= created_updated_before,
                )
            )
            .order_by(sql_model.SpireAisData.created_at.asc())
        )
        result = session.execute(stmt)
        return pd.DataFrame(
            result,
            columns=[
                "id",
                "spire_update_statement",
                "vessel_mmsi",
                "vessel_name",
                "vessel_imo",
                "vessel_callsign",
                "vessel_id",
                "position_accuracy",
                "position_collection_type",
                "position_course",
                "position_heading",
                "position_latitude",
                "position_longitude",
                "position_maneuver",
                "position_navigational_status",
                "position_rot",
                "position_speed",
                "position_timestamp",
                "position_update_timestamp",
                "created_at",
            ],
        )

    def get_all_data_between_date_bis(
        self,
        session: Session,
        created_updated_after: datetime,
        created_updated_before: datetime,
    ) -> pd.DataFrame:
        stmt = (
            select(
                sql_model.SpireAisData.id,
                sql_model.SpireAisData.spire_update_statement,
                sql_model.SpireAisData.vessel_mmsi,
                sql_model.SpireAisData.vessel_name,
                sql_model.SpireAisData.vessel_imo,
                sql_model.SpireAisData.vessel_callsign,
                sql_model.Vessel.id,
                sql_model.SpireAisData.position_accuracy,
                sql_model.SpireAisData.position_collection_type,
                sql_model.SpireAisData.position_course,
                sql_model.SpireAisData.position_heading,
                sql_model.SpireAisData.position_latitude,
                sql_model.SpireAisData.position_longitude,
                sql_model.SpireAisData.position_maneuver,
                sql_model.SpireAisData.position_navigational_status,
                sql_model.SpireAisData.position_rot,
                sql_model.SpireAisData.position_speed,
                sql_model.SpireAisData.position_timestamp,
                sql_model.SpireAisData.position_update_timestamp,
                sql_model.SpireAisData.created_at,
            )
            .join(
                sql_model.Vessel,
                sql_model.Vessel.mmsi == sql_model.SpireAisData.vessel_mmsi,
            )
            .where(
                and_(
                    sql_model.Vessel.tracking_activated == True,
                    sql_model.SpireAisData.created_at > created_updated_after,
                    sql_model.SpireAisData.created_at <= created_updated_before,
                )
            )
            .order_by(sql_model.SpireAisData.created_at.asc())
        )
        result = session.execute(stmt)
        return pd.DataFrame(
            result,
            columns=[
                "id",
                "spire_update_statement",
                "vessel_mmsi",
                "vessel_name",
                "vessel_imo",
                "vessel_callsign",
                "vessel_id",
                "position_accuracy",
                "position_collection_type",
                "position_course",
                "position_heading",
                "position_latitude",
                "position_longitude",
                "position_maneuver",
                "position_navigational_status",
                "position_rot",
                "position_speed",
                "position_timestamp",
                "position_update_timestamp",
                "created_at",
            ],
        )

    def get_all_data_by_mmsi(
            self,
            session: Session,
            mmsi: int,
            order_by: str = None,
            created_updated_after: datetime = None,
    ) -> list[SpireAisData]:
        stmt = select(sql_model.SpireAisData).where(
            sql_model.SpireAisData.vessel_mmsi == mmsi
        )
        if created_updated_after:
            stmt = stmt.where(
                sql_model.SpireAisData.created_at >= created_updated_after
            )

        if order_by == SpireAisDataRepository.ORDER_BY_VESSEL:
            stmt = stmt.order_by(sql_model.SpireAisData.vessel_timestamp.asc())
        elif order_by == SpireAisDataRepository.ORDER_BY_POSITION:
            stmt = stmt.order_by(sql_model.SpireAisData.position_timestamp.asc())
        elif order_by == SpireAisDataRepository.ORDER_BY_VOYAGE:
            stmt = stmt.order_by(sql_model.SpireAisData.voyage_timestamp.asc())
        result = session.execute(stmt).scalars()
        return [SpireAisDataRepository.map_to_domain(e) for e in result]

    @staticmethod
    def map_to_orm(data: SpireAisData) -> sql_model.SpireAisData:
        return sql_model.SpireAisData(**data.__dict__)

    @staticmethod
    def map_to_domain(orm_data: sql_model.SpireAisData) -> SpireAisData:
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
