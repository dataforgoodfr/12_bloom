import pandas as pd
import geopandas as gpd
import numpy as np
from geopandas.tools import sjoin
from shapely.geometry import Point, MultiPolygon, Polygon
from shapely import wkt
import time
import folium
import json
from copy import copy
import fiona
from typing import Union
from geopandas import GeoDataFrame, GeoSeries
from typing import Optional



class Polygons:

    def __init__(self):
        pass

    def load_shp(self,path):
        self.data = gpd.GeoDataFrame.from_file(path) 

    def load_gpkg(self, path, target_crs='EPSG:3857'):
        layer_list = []

        for layername in fiona.listlayers(path):
            geopkg = gpd.read_file(path, layer=layername)
            if target_crs:
                geopkg = geopkg.to_crs(target_crs)
            layer_list.append(geopkg)

        self.data = pd.concat(layer_list, ignore_index=True)

    def plot(self, interactive=False):
        if interactive:
            self.plot_interactive()
        else:
            self.data.plot()

    def plot_interactive(self,popup_name = None,map_center = (0,0)):
        # Create a Folium map
        # map_center = self.data.geometry.centroid.iloc[0].coords[:][0][::-1]  # Calculate map center from the first polygon's centroid

        poly_map = folium.Map(location=map_center, zoom_start=4)

        # Add polygons to the map
        for _, poly in self.data.iterrows():
            geojson = folium.GeoJson(
                poly.geometry,
                style_function=lambda x: {
                    'color': 'blue',
                    'fillColor': 'blue',
                    'fillOpacity': 0.5,
                    'weight': 1
                }
            )
            if isinstance(popup_name,str):
                geojson.add_child(folium.Popup(poly[popup_name]))  # Add a popup with the name, adjust 'name' to the appropriate column name in your dataset
            geojson.add_to(poly_map)

        # Show the map
        return poly_map

    def simplify_geometries(self, tolerance: Optional[float] = 0.001) -> None:
        """
        Simplifies the geometries of the polygons in the Polygons class.

        This method applies the Douglas-Peucker simplification algorithm
        to reduce the number of vertices in the geometries. Simplification
        may result in a loss of detail in the geometries, but can improve
        the performance of spatial operations like buffering.

        Args:
            tolerance (float, optional): The tolerance value used in the simplification
                process. A higher value results in more aggressive simplification.
                Default value is 0.001.

        Returns:
            None
        """
        self.data.geometry = self.data.geometry.simplify(tolerance)


    def filter_by_attribute(self, attribute, value):
        self.data = self.data[self.data[attribute] == value]

    def attribute_stats(self, attribute):
        return self.data[attribute].describe()

    def compute_areas(self):
        self.data['area'] = self.data.geometry.area

    def buffer_polygons(self, distance):
        self.data.geometry = self.data.geometry.buffer(distance)