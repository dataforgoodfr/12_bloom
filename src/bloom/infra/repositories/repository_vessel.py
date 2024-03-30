from contextlib import AbstractContextManager
from typing import Any, Generator, Union

import geopandas as gpd
import pandas as pd
from bloom.domain.vessel import Vessel
from bloom.domain.vessels.vessel_trajectory import VesselTrajectory
from bloom.infra.database import sql_model
from bloom.logger import logger
from dependency_injector.providers import Callable
from shapely import Point, wkb
from sqlalchemy.orm import Session
from sqlalchemy import select


class VesselRepository:
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def get_vessels_list(self, session: Session) -> list[Vessel]:
        """
        Liste l'ensemble des vessels actifs
        """
        stmt = select(sql_model.Vessel).where(sql_model.Vessel.tracking_activated == True)
        e = session.execute(stmt).scalars()
        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    def batch_create_vessel(self, session: Session, ports: list[Vessel]) -> list[Vessel]:
        orm_list = [VesselRepository.map_to_sql(port) for port in ports]
        session.add_all(orm_list)
        return [VesselRepository.map_to_domain(orm) for orm in orm_list]

    def get_all_vessels_list(self, session: Session) -> list[Vessel]:
        """
        Liste l'ensemble des vessels actifs ou inactifs
        """
        stmt = select(sql_model.Vessel)
        e = session.execute(stmt).scalars()

        if not e:
            return []
        return [VesselRepository.map_to_domain(vessel) for vessel in e]

    @staticmethod
    def map_to_domain(sql_vessel: sql_model.Vessel) -> Vessel:
        return Vessel(
            id=sql_vessel.id,
            mmsi=sql_vessel.mmsi,
            ship_name=sql_vessel.ship_name,
            width=sql_vessel.width,
            length=sql_vessel.length,
            country_iso3=sql_vessel.country_iso3,
            type=sql_vessel.type,
            imo=sql_vessel.imo,
            cfr=sql_vessel.cfr,
            registration_number=sql_vessel.registration_number,
            external_marking=sql_vessel.external_marking,
            ircs=sql_vessel.ircs,
            tracking_activated=sql_vessel.tracking_activated,
            tracking_status=sql_vessel.tracking_status,
            home_port_id=sql_vessel.home_port_id,
            created_at=sql_vessel.created_at,
            updated_at=sql_vessel.updated_at,
        )

    @staticmethod
    def map_to_sql(vessel: Vessel) -> sql_model.Vessel:
        return sql_model.Vessel(
            id=vessel.id,
            mmsi=vessel.mmsi,
            ship_name=vessel.ship_name,
            width=vessel.width,
            length=vessel.length,
            country_iso3=vessel.country_iso3,
            type=vessel.type,
            imo=vessel.imo,
            cfr=vessel.cfr,
            registration_number=vessel.registration_number,
            external_marking=vessel.external_marking,
            ircs=vessel.ircs,
            tracking_activated=vessel.tracking_activated,
            tracking_status=vessel.tracking_status,
            home_port_id=vessel.home_port_id,
            created_at=vessel.created_at,
            updated_at=vessel.updated_at,
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

    def get_all_spire_vessels_position(
            self,
            session: Session,
            batch_size: int,
    ) -> Generator[sql_model.VesselPositionSpire, None, None]:
        yield from session.query(sql_model.VesselPositionSpire).yield_per(batch_size)

    def get_vessel_trajectory(
            self,
            mmsi: str,
            as_trajectory: bool = True,
    ) -> Union[Point, None]:
        def convert_wkb_to_point(x: Any) -> Union[Point, None]:
            try:
                point = wkb.loads(bytes(x.data))
                return point  # noqa: TRY300
            except:  # noqa: E722
                return None

        with self.session_factory() as session:
            vessel = session.query(sql_model.Vessel).filter_by(mmsi=mmsi).first()
            positions = self.get_all_positions(mmsi, session) if vessel is not None else []

        if not positions:
            # Create empty dataframe with expected columns when vessel has no trajectory
            df = pd.DataFrame(
                columns=[
                    "timestamp",
                    "ship_name",
                    "IMO",
                    "vessel_id",
                    "mmsi",
                    "last_position_time",
                    "position",
                    "speed",
                    "navigation_status",
                    "vessel_length",
                    "vessel_width",
                    "voyage_destination",
                    "voyage_draught",
                    "voyage_eta",
                    "accuracy",
                    "position_sensors",
                    "course",
                    "heading",
                    "rot",
                ]
            )
            df = df.astype({"timestamp": "datetime64[ms]"})
        else:
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
        # df.loc[df["timestamp"] <= "2023-06-28 14:44:00", "geometry"] = df[
        #    "geometry"
        # ].apply(lambda point: Point(point.y, point.x))

        df["is_fishing"] = df["navigation_status"] == "ENGAGED_IN_FISHING"

        # Create a boolean Series where True represents a change from 'MOORED' to something else
        condition = (df["navigation_status"].shift() == "MOORED") & (
                df["navigation_status"] != "MOORED"
        )

        # Use cumsum to generate the 'voyage_id'.
        # The cumsum operation works because 'True' is treated as 1 and 'False' as 0.
        df["voyage_id"] = condition.cumsum()

        positions = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        metadata = {k: v for k, v in vessel.__dict__.items() if k != "_sa_instance_state"}

        if as_trajectory:
            trajectory = VesselTrajectory(metadata, positions)
            return trajectory
        else:
            return metadata, positions
