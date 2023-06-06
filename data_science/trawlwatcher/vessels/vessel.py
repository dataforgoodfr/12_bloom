

import folium
from datetime import datetime
import pandas as pd
import random
from tqdm.auto import tqdm
import geopandas as gpd
from shapely.geometry import Point
from .vessel_utils.trajectory import visualize


class Vessel:
    def __init__(self, 
                 data: gpd.GeoDataFrame = None,
                 vessel_id = None,
                 chunk_id = 0):
        self.vessel_id = vessel_id
        self.data = data
        if isinstance(self.data, gpd.GeoDataFrame):
            self.data["chunk_id"] = chunk_id

    def __repr__(self):
        n_chunk = len(self.data["chunk_id"].unique())
        return f"Vessel(n_points={len(self.data)},n_chunks={n_chunk})"

    def load_long_lat_from_path(self, path, crs = "EPSG:3857"):
        pandas_df =  pd.DataFrame.from_file(path) 
        geometry = [Point(xy) for xy in zip(pandas_df['lon'], pandas_df['lat'])]
        self.data = gpd.GeoDataFrame(pandas_df, crs=crs, geometry=geometry)
    
    def load_long_lat_from_pandas(self, pandas_df: pd.DataFrame, crs = "EPSG:3857"):
        geometry = [Point(xy) for xy in zip(pandas_df['lon'], pandas_df['lat'])]
        self.data = gpd.GeoDataFrame(pandas_df, crs=crs, geometry=geometry)

    def visualize_trajectory(self, color_by_speed: bool = False, marker_by_fishing: bool = False,**kwargs):
        return visualize(self.data,color_by_speed,marker_by_fishing,**kwargs)

    def query(self, query_str, reset_chunk_id: bool = False):
        filtered_data = self.data.query(query_str)
        assert len(filtered_data) > 0
        if(reset_chunk_id):
             filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id)
        else: 
            filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id, filtered_data["chunk_id"])
        return filtered_vessel

    def filter_by_date(self, start_date: datetime, end_date: datetime, reset_chunk_id: bool = False):
        # Filter the data by the specified date range
        filtered_data = self.data[(self.data['timestamp'] >= start_date) & (self.data['timestamp'] <= end_date)]
        # Create a new Vessel object with the filtered data
        if(reset_chunk_id):
             filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id)
        else: 
            filtered_vessel = Vessel(filtered_data.copy(),self.vessel_id, filtered_data["chunk_id"])
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

    def sample(self, n: int = 1, reset_chunk_id: bool = False):
        all_chunk_ids = list(self.data["chunk_id"].unique())
        if n > len(all_chunk_ids):
            n = len(all_chunk_ids)
        chunk_ids = random.sample(list(self.data["chunk_id"].unique()), n)
        return self.query(f"chunk_id in {chunk_ids}", reset_chunk_id)


    def is_in_zone(self,polygons,how = "inner"):
        return self.data.sjoin(polygons.data,how = how)