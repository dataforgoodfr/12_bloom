import random
from datetime import datetime

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint

from bloom.domain.zones.mpa import (
    add_closest_marine_protected_areas,
    get_closest_marine_protected_areas,
)

from .visualize_trajectory import visualize

ANGLE = 180


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Calculate the bearing between two points
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    y = np.sin(dlon) * np.cos(lat2)
    initial_bearing = np.arctan2(y, x)
    initial_bearing = np.degrees(initial_bearing)
    return (initial_bearing + 360) % 360


def normalize_bearing(angle: float) -> float:
    """
    Normalize a bearing difference to be within the range of -180 to 180.
    """
    while angle <= -ANGLE:
        angle += 360
    while angle > ANGLE:
        angle -= 360
    return angle


class VesselTrajectory:
    def __init__(self, metadata: pd.DataFrame, positions: gpd.GeoDataFrame) -> None:
        self.metadata = metadata
        self.positions = positions

        self.chunk_data(24)

        if not self.positions.empty:
            # Warning in CRS 4326 - the order is longitude,latitude
            self.positions["lat"] = self.positions["geometry"].map(lambda pos: pos.y)
            self.positions["lon"] = self.positions["geometry"].map(lambda pos: pos.x)
            self.positions = self.compute_angle(self.positions)
            self.positions = self.compute_change_direction_flag(self.positions, 50)
            self.positions = self.compute_change_direction_flag(self.positions, 150)
            self.positions = self.compute_rolling_deviation(self.positions, "3H")

    # def __init__(self, data: pd.DataFrame,vessel_id = None,crs = "EPSG:3857"):

    # # Convert the dataset to a GeoDataFrame

    def __repr__(self) -> str:
        return f"""Vessel(n_points={len(self.positions)},
            n_voyages={self.n_voyages},n_chunks={self.n_chunks})"""

    @property
    def n_voyages(self) -> int:
        return self.positions["voyage_id"].nunique()

    @property
    def n_chunks(self) -> int:
        return self.positions["chunk_id"].nunique()

    @property
    def centroid(self) -> tuple[float, float]:
          # Make sure that your GeoDataFrame is named gdf and has a column 'geometry'
        all_points = MultiPoint(self.positions["geometry"].unary_union)
        centroid = all_points.centroid

        # Warning in CRS 4326 - the order is longitude,latitude
        return (centroid.y, centroid.x)

    @property
    def mpas(self) -> []:
        if hasattr(self, "_mpas"):
            return self._mpas
        return None

    @mpas.setter
    def mpas(self, value:[])->None:
        self._mpas = value

    def get_closest_marine_protected_areas(self, radius: int = 100) -> None:
        self._mpas, self._mpas_gdf = get_closest_marine_protected_areas(
            self.centroid,
            radius,
        )

    def visualize_trajectory(
        self,
        color_by_speed: bool = False,
        marker_by_fishing: bool = False,
        show_mpas: bool = True,
        show_iucn: bool = True,
        **kwargs: any,
    ) -> folium.Map:
        m = visualize(self.positions, color_by_speed, marker_by_fishing, **kwargs)
        if self.mpas is not None and show_mpas:
            add_closest_marine_protected_areas(self.mpas, m, show_iucn=show_iucn)
        return m

    def query(
        self,
        query_str: str = None,
        chunk_id: str = None,
        voyage_id: str = None,
    ) -> "VesselTrajectory":
        if query_str is not None:
            pass
        elif chunk_id is not None:
            query_str = f"chunk_id=={chunk_id}"
        elif voyage_id is not None:
            query_str = f"voyage_id=={voyage_id}"

        filtered_data = self.positions.query(query_str)
        assert len(filtered_data) > 0
        filtered_vessel = VesselTrajectory(self.metadata, filtered_data.copy())

        filtered_vessel.mpas = self.mpas

        filtered_vessel.positions.index = filtered_data.index

        return filtered_vessel

    def filter_by_date(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> "VesselTrajectory":
        # Filter the data by the specified date range
        filtered_data = self.positions[
            (self.positions["timestamp"] >= start_date)
            & (self.positions["timestamp"] <= end_date)
        ]
        # Create a new Vessel object with the filtered data
        return VesselTrajectory(self.metadata, filtered_data.copy())

    def chunk_data(self, max_duration_hours: int) -> None:
        # Calculate the duration of each chunk in seconds
        max_duration_seconds = max_duration_hours * 3600

        # Calculate the time deltas between successive rows
        time_deltas = self.positions["timestamp"].diff(1).fillna(pd.Timedelta(0))

        # Calculate the cumulative time deltas
        cum_time_deltas = time_deltas.cumsum()

        # Calculate the chunk IDs based on the cumulative
        # time deltas and the maximum duration
        chunk_ids = (cum_time_deltas.dt.total_seconds() // max_duration_seconds).astype(
            int,
        )

        # Assign consecutive chunk IDs based on the order
        # in which they appear in the data
        rank = chunk_ids.rank(method="dense").astype(int)
        consecutive_chunk_ids = rank - rank.min()

        # Add the consecutive chunk IDs to the dataframe
        self.positions["chunk_id"] = consecutive_chunk_ids

    def sample(self) -> "VesselTrajectory":
        chunk_id = random.choice(list(self.positions["chunk_id"].unique()))
        return self.query(f"chunk_id=={chunk_id}")

    def is_in_mpas(
        self,
        mpas_gdf: gpd.GeoDataFrame = None,
        how: str = "inner",
    ) -> gpd.GeoDataFrame:
        if mpas_gdf is None:
            mpas_gdf = self._mpas_gdf

        return self.positions.sjoin(
            mpas_gdf,
            how=how,
            predicate="intersects",
        ).drop_duplicates(subset="timestamp")

    def compute_angle(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        # Now, compute the bearings
        gdf["bearing"] = calculate_bearing(
            gdf["lat"].shift(),
            gdf["lon"].shift(),
            gdf["lat"],
            gdf["lon"],
        )

        # Compute the change in bearings
        gdf["angle"] = gdf["bearing"].diff()
        gdf["angle"] = gdf["angle"].map(normalize_bearing)
        gdf["angle_abs"] = gdf["angle"].abs()
        return gdf

    def compute_change_direction_flag(
        self,
        gdf: gpd.GeoDataFrame,
        threshold: str = 30,
    ) -> gpd.GeoDataFrame:
        if "angle" not in gdf.columns:
            gdf = self.compute_angle(gdf)
        gdf[f"flag_change_{threshold}"] = (gdf["angle"].abs() > threshold).astype(int)
        return gdf

    def compute_rolling_deviation(
        self,
        gdf: gpd.GeoDataFrame,
        period: str = "3H",
    ) -> gpd.GeoDataFrame:
        # Ensure your 'timestamp' column is of datetime type
        gdf["timestamp"] = pd.to_datetime(gdf["timestamp"])

        # Set timestamp column as index
        gdf = gdf.set_index("timestamp")

        # Calculate the rolling standard deviation for 'bearing_change'
        gdf[f"rolling_angle_{period}"] = gdf["angle"].rolling(period).std()

        return gdf.reset_index()  # Reset index if necessary


# # For the second flag, we can use a rolling window
# to check for consistent increases or decreases in latitude

# # Create the second flag if either condition is met

# # You may want to do the same for the 'lon' variable,
# depending on the trajectories you're dealing with
