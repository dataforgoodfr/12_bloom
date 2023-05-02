import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, MultiPolygon, Polygon, LineString
from shapely.ops import nearest_points
import time
import folium
from vincenty import vincenty

from .cache import download_and_cache_file

URL = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_coastline.zip"
# URL = "https://github.com/nvkelso/natural-earth-vector/raw/master/10m_physical/ne_10m_coastline.shp"

class Coastlines:

    def __init__(self):

        # Download, cache and reads file
        path = download_and_cache_file(URL)
        self.data = gpd.read_file(path)

        # transform it to Web Mercator projection
        self.data_mercator = self.data.to_crs('EPSG:3857')

    def plot(self):
        self.data.plot()