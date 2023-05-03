from contextlib import AbstractContextManager
from pathlib import Path

import pandas as pd
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape

from bloom.config import settings
from bloom.domain.vessel import AbstractVessel, Vessel, VesselPositionMarineTraffic
from bloom.infra.database import sql_model
from bloom.logger import logger


class RepositoryVessel(AbstractVessel):
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory
        self.vessels_path = Path.joinpath(Path.cwd(), "data/chalutiers_pelagiques.csv")

    def load_vessel_identifiers(self) -> list[Vessel]:
        with self.session_factory() as session:
            e = session.query(sql_model.Vessel).all()
            if not e:
                return []
            return [self.map_sql_vessel_to_schema(vessel) for vessel in e]

    def load_vessel_identifiers_from_file(self) -> list[Vessel]:
        df = pd.read_csv(self.vessels_path, sep=";")
        vessel_identifiers_list = df["IMO"].tolist()
        return [Vessel(IMO=imo) for imo in vessel_identifiers_list]

    def save_vessels_positions(
        self,
        vessels_positions_list: list[VesselPositionMarineTraffic],
    ) -> None:
        with self.session_factory() as session:
            sql_vessel_position_objects = [
                self.map_schema_marine_traffic_to_sql_vessel_position(vessel)
                for vessel in vessels_positions_list
            ]
            session.add_all(sql_vessel_position_objects)
            session.commit()
            logger.info(
                f"{len(sql_vessel_position_objects)} "
                f"positions have been saved in base.",
            )

    @staticmethod
    def map_sql_vessel_to_schema(sql_vessel: sql_model.Vessel) -> Vessel:
        return Vessel(
            vessel_id=sql_vessel.id,
            ship_name=sql_vessel.ship_name,
            IMO=sql_vessel.IMO,
            mmsi=sql_vessel.mmsi,
        )

    @staticmethod
    def map_schema_marine_traffic_to_sql_vessel_position(
        vessel_position: VesselPositionMarineTraffic,
    ) -> sql_model.VesselPositionMarineTraffic:
        return sql_model.VesselPositionMarineTraffic(
            timestamp=vessel_position.timestamp,
            ship_name=vessel_position.ship_name,
            IMO=vessel_position.IMO,
            vessel_id=vessel_position.vessel_id,
            mmsi=vessel_position.mmsi,
            last_position_time=vessel_position.last_position_time,
            fishing=vessel_position.fishing,
            at_port=vessel_position.at_port,
            port_name=vessel_position.current_port,
            position=from_shape(vessel_position.position, srid=settings.srid),
            status=vessel_position.status,
            speed=vessel_position.speed,
            navigation_status=vessel_position.navigation_status,
        )
