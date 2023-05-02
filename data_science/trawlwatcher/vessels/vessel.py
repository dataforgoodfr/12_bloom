

import folium
from datetime import datetime
import pandas as pd
import random
from tqdm.auto import tqdm
import geopandas as gpd
from shapely.geometry import Point
from .trajectory import visualize


class Vessel:
    def __init__(self, data: pd.DataFrame,vessel_id = None,crs = "EPSG:3857"):
        self.vessel_id = vessel_id
        self.data = data
        self.data["chunk_id"] = 0

        # Convert the dataset to a GeoDataFrame
        geometry = [Point(xy) for xy in zip(self.data['lon'], self.data['lat'])]
        self.data = gpd.GeoDataFrame(self.data, crs=crs, geometry=geometry)

    def __repr__(self):
        n_chunk = self.data["chunk_id"].max() + 1
        return f"Vessel(n_points={len(self.data)},n_chunks={n_chunk})"


    def visualize_trajectory(self,color_by_speed: bool = False, marker_by_fishing: bool = False,**kwargs):
        return visualize(self.data,color_by_speed,marker_by_fishing,**kwargs)

    def query(self,query_str):
        filtered_data = self.data.query(query_str)
        assert len(filtered_data) > 0
        filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id)
        return filtered_vessel

    def filter_by_date(self, start_date: datetime, end_date: datetime):
        # Filter the data by the specified date range
        filtered_data = self.data[(self.data['timestamp'] >= start_date) & (self.data['timestamp'] <= end_date)]
        # Create a new Vessel object with the filtered data
        filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id)

        return filtered_vessel


    def chunk_data(self, max_duration_hours: int):
        # Calculate the duration of each chunk in seconds
        max_duration_seconds = max_duration_hours * 3600
    
        # Calculate the time deltas between successive rows
        time_deltas = self.data['timestamp'].diff(1).fillna(pd.Timedelta(0))

        # Calculate the cumulative time deltas
        cum_time_deltas = time_deltas.cumsum()

        # Calculate the chunk IDs based on the cumulative time deltas and the maximum duration
        chunk_ids = (cum_time_deltas.dt.total_seconds() // max_duration_seconds).astype(int)

        # Assign consecutive chunk IDs based on the order in which they appear in the data
        rank = chunk_ids.rank(method='dense').astype(int)
        consecutive_chunk_ids = rank - rank.min()

        # Add the consecutive chunk IDs to the dataframe
        self.data['chunk_id'] = consecutive_chunk_ids


    def sample(self):
        chunk_id = random.choice(list(self.data["chunk_id"].unique()))
        return self.query(f"chunk_id=={chunk_id}")


    def is_in_zone(self,polygons,how = "inner"):
        return self.data.sjoin(polygons.data,how = how)