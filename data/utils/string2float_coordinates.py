import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

csv_input = os.path.join(os.path.dirname(__file__), "../ports.csv")
csv_output = os.path.join(os.path.dirname(__file__), "../ports.csv")


def convert_coords(coord):
    """
    Convert a string coordinate to a float coordinate
    """
    if "N" in coord or "E" in coord:
        return float(coord.replace("N", "").replace("E", ""))
    elif "S" in coord or "W" in coord:
        return float(coord.replace("S", "").replace("W", "")) * -1
    else:
        return float(coord)


df = pd.read_csv(csv_input, sep=";")

# Clean the latitude and longitude columns
df["latitude"] = df["latitude"].apply(convert_coords)
df["longitude"] = df["longitude"].apply(convert_coords)

# Create a geometry column
df["geometry_point"] = [Point(xy) for xy in zip(df.longitude, df.latitude)]

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
print(gdf.head())

gdf.to_csv(csv_output, index=False, sep=";")
