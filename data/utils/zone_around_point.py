"""
Another method with geodesic to have exactly radius_m meters around a port, no matter where on
the globe (polygons of the ports in the north seams to be flat, it's normal, it's the
projection)
"""

import os
import geopandas as gpd
import pandas as pd
import pyproj
from shapely import wkt
from shapely.geometry import Polygon
from pathlib import Path

radius_m = 3000  # Radius in kilometers
resolution = 10  # Number of points in the resulting polygon
crs_epsg = 4326  # CRS for WGS84

csv_input = Path(__file__).parent.joinpath("../ports.csv")
csv_output = Path(__file__).parent.joinpath(f"../ports_rad{radius_m}_res{resolution}.csv")

# Load CSV into DataFrame and convert WKT to geometry
df = pd.read_csv(csv_input, sep=";")
df["geometry_point"] = df["geometry_point"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry="geometry_point", crs=crs_epsg)

# Function to create geodesic buffer around a point
def geodesic_point_buffer(lat, lon, radius_m, resolution):
    """
    Input
    lat: latitude of the center point
    lon: longitude of the center point
    radius_m: radius of the buffer in meters
    resolution: number of points in the resulting polygon
    """
    geod = pyproj.Geod(ellps="WGS84")  # Define the ellipsoid
    # Create a circle in geodesic coordinates
    angles = range(0, 360, 360 // resolution)
    circle_points = []
    for angle in angles:
        # Calculate the point on the circle for this angle
        lon2, lat2, _ = geod.fwd(lon, lat, angle, radius_m)
        circle_points.append((lon2, lat2))
    # Create a polygon from these points
    return Polygon(circle_points)


# Apply the buffer function to create geodesic buffers
gdf["geometry_buffer"] = gdf.apply(
    lambda row: geodesic_point_buffer(
        float(row["latitude"]),
        float(row["longitude"]),
        radius_m,
        resolution,
    ),
    axis=1,
)

# Save the GeoDataFrame with buffers to a new CSV file
gdf.to_csv(csv_output, index=False, sep=";")