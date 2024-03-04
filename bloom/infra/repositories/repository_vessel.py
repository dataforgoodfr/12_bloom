from contextlib import AbstractContextManager
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from dependency_injector.providers import Callable
from geoalchemy2.shape import from_shape
from shapely import Point, wkb
from sqlalchemy.orm import Session

from bloom.config import settings
from bloom.domain.vessel import Vessel, VesselPositionMarineTraffic
from bloom.domain.vessels.vessel_trajectory import VesselTrajectory
from bloom.infra.database import sql_model
from bloom.logger import logger


class RepositoryVessel:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory
        self.vessels_path = Path.joinpath(Path.cwd(), "data/chalutiers_pelagiques.csv")

    def load_vessel_metadata(self) -> list[Vessel]:
        with self.session_factory() as session:
            e = session.query(sql_model.Vessel).filter(
                sql_model.Vessel.mt_activated == True,  # noqa: E712
                sql_model.Vessel.mmsi != None,  # noqa: E711
                # sqlAlchemy doesn't tolerate is True
            )
            if not e:
                return []
            return [self.map_sql_vessel_to_schema(vessel) for vessel in e]

    def load_all_vessel_metadata(self) -> list[Vessel]:
        with self.session_factory() as session:
            e = session.query(sql_model.Vessel).filter(
                sql_model.Vessel.mmsi != None,  # noqa: E711
            )
            if not e:
                return []
            return [self.map_sql_vessel_to_schema(vessel) for vessel in e]

    def load_vessel_metadata_from_file(self) -> list[Vessel]:
        df = pd.read_csv(self.vessels_path, sep=";")
        vessel_identifiers_list = df["mmsi"].tolist()
        return [Vessel(mmsi=mmsi) for mmsi in vessel_identifiers_list]

    def save_marine_traffic_vessels_positions(
        self,
        vessels_positions_list: list[VesselPositionMarineTraffic],
        timestamp: datetime,
        # according to me, domain class is useless here if we have two tables
    ) -> None:
        with self.session_factory() as session:
            sql_vessel_position_objects = [
                self.map_schema_marine_traffic_to_sql_vessel_position(vessel, timestamp)
                for vessel in vessels_positions_list
            ]
            session.add_all(sql_vessel_position_objects)
            session.commit()
            logger.info(
                f"{len(sql_vessel_position_objects)} "
                f"positions have been saved in base.",
            )

    def save_spire_vessels_positions(
        self,
        sql_vessels_positions_list: list[sql_model.VesselPositionSpire],
    ) -> None:
        with self.session_factory() as session:
            session.add_all(sql_vessels_positions_list)
            session.commit()
            logger.info(
                f"{len(sql_vessels_positions_list)} "
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
    def map_json_vessel_to_sql_spire(
        vessel: str,
        vessel_id: int,
        timestamp: datetime,
    ) -> sql_model.VesselPositionSpire:
        return sql_model.VesselPositionSpire(
            timestamp=timestamp,
            ship_name=vessel["staticData"]["name"],
            IMO=vessel["staticData"]["imo"],
            vessel_id=vessel_id,
            mmsi=vessel["staticData"]["mmsi"],
            last_position_time=(
                vessel["lastPositionUpdate"]["timestamp"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            position=(
                from_shape(
                    Point(
                        vessel["lastPositionUpdate"]["longitude"],
                        vessel["lastPositionUpdate"]["latitude"],
                    ),
                    srid=settings.srid,
                )
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            speed=(
                vessel["lastPositionUpdate"]["speed"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            navigation_status=(
                vessel["lastPositionUpdate"]["navigationalStatus"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            vessel_length=(
                vessel["staticData"]["dimensions"]["width"]
                if vessel["staticData"]["dimensions"] is not None
                else None
            ),
            vessel_width=(
                vessel["staticData"]["dimensions"]["length"]
                if vessel["staticData"]["dimensions"] is not None
                else None
            ),
            voyage_destination=(
                vessel["currentVoyage"]["destination"]
                if vessel["currentVoyage"] is not None
                else None
            ),
            voyage_draught=(
                vessel["currentVoyage"]["draught"]
                if vessel["currentVoyage"] is not None
                else None
            ),
            voyage_eta=(
                vessel["currentVoyage"]["eta"]
                if vessel["currentVoyage"] is not None
                else None
            ),
            accuracy=(
                vessel["lastPositionUpdate"]["accuracy"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            position_sensors=(
                vessel["lastPositionUpdate"]["collectionType"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            course=(
                vessel["lastPositionUpdate"]["course"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            heading=(
                vessel["lastPositionUpdate"]["heading"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
            rot=(
                vessel["lastPositionUpdate"]["rot"]
                if vessel["lastPositionUpdate"] is not None
                else None
            ),
        )

    @staticmethod
    def map_schema_marine_traffic_to_sql_vessel_position(
        vessel_position: VesselPositionMarineTraffic,
        timestamp: datetime,
    ) -> sql_model.VesselPositionMarineTraffic:
        return sql_model.VesselPositionMarineTraffic(
            timestamp=timestamp,
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

    def get_all_positions(
        self,
        mmsi: str,
        session: Session,
    ) -> list[sql_model.VesselPositionSpire]:
        positions = (
            session.query(sql_model.VesselPositionSpire)
            .filter(sql_model.VesselPositionSpire.mmsi == mmsi)
            .all()
        )
        if positions:
            return positions
        else:
            return []

    def get_vessel_trajectory(
        self,
        mmsi: str,
        as_trajectory: bool = True,
    ) -> Point | None: #Point ?
        def convert_wkb_to_point(x: Any) -> Point | None:
            try:
                point = wkb.loads(bytes(x.data))
                return point  # noqa: TRY300
            except:  # noqa: E722
                return None

        with self.session_factory() as session:
            vessel = session.query(sql_model.Vessel).filter_by(mmsi=mmsi).first()
            positions = (
                self.get_all_positions(mmsi, session) if vessel is not None else []
            )

        df = (
            pd.DataFrame([p.__dict__ for p in positions])
            .drop(columns=["_sa_instance_state"])
            .sort_values("timestamp")
            .drop_duplicates(subset=["mmsi", "timestamp"])
            .reset_index(drop=True)
        )

        df["geometry"] = df["position"].map(convert_wkb_to_point)

        # With CRS 4326, the coordinates are reversed
        # Temporary fix
        #df.loc[df["timestamp"] <= "2023-06-28 14:44:00", "geometry"] = df[
        #    "geometry"
        #].apply(lambda point: Point(point.y, point.x))

        df["is_fishing"] = df["navigation_status"] == "ENGAGED_IN_FISHING"

        # Create a boolean Series where True represents a change from 'MOORED' to something else
        condition = (df["navigation_status"].shift() == "MOORED") & (
            df["navigation_status"] != "MOORED"
        )

        # Use cumsum to generate the 'voyage_id'.
        # The cumsum operation works because 'True' is treated as 1 and 'False' as 0.
        df["voyage_id"] = condition.cumsum()

        positions = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        metadata = {
            k: v for k, v in vessel.__dict__.items() if k != "_sa_instance_state"
        }

        if as_trajectory:
            trajectory = VesselTrajectory(metadata, positions)
            return trajectory
        else:
            return metadata, positions
