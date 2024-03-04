from typing import Any

import folium
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
from folium.plugins import AntPath


def visualize(
    data: gpd.GeoDataFrame,
    marker_by_fishing: bool = False,
    with_animation: bool = False,
    min_speed: float = 2.0,
    max_speed: float = None,
    weight: float = 5,
    minutes_ais: int = 120,
    cmap: Any = plt.cm.Spectral_r,
) -> folium.Map:
    # Create a map centered on the first latitude/longitude position
    map_center = [data.iloc[0]["lat"], data.iloc[0]["lon"]]
    m = folium.Map(location=map_center, zoom_start=6)

    # Add markers for the first and last points
    folium.Marker(
        location=[data.iloc[0]["lat"], data.iloc[0]["lon"]],
        icon=folium.Icon(icon="play", color="blue", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        location=[data.iloc[-1]["lat"], data.iloc[-1]["lon"]],
        icon=folium.Icon(icon="stop", color="red"),
    ).add_to(m)

    # Add markers for each data point only when the boat is fishing
    if marker_by_fishing:
        for _i, row in data.iterrows():
            if row["is_fishing"] > 0:
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    icon=folium.Icon(icon="fish", color="blue", prefix="fa"),
                ).add_to(m)

    # Define a function to color the polyline based on speed
    def speed_color(speed: float, cmap: Any = cmap) -> str:
        rgba = cmap(speed)
        return mcolors.rgb2hex(rgba)

    def antpath_delay(
        speed: float,
        min_delay: int = 1000,
        max_delay: int = 20000,
    ) -> float:
        return min_delay + (1 - speed) * (max_delay - min_delay)

    if max_speed is None:
        max_speed = data["speed"].max()

    speeds = data["speed"].clip(min_speed, max_speed)
    normalized_speeds = (speeds - min_speed) / (max_speed - min_speed)
    colors = normalized_speeds.map(speed_color).tolist()
    delays = normalized_speeds.map(antpath_delay).tolist()

    stop_condition = (
        (data["timestamp"] - data["last_position_time"])
        >= pd.Timedelta(minutes=minutes_ais)
    ).tolist()

    if not with_animation:
        # Add lines connecting each latitude/longitude point with a color based on speed
        for i in range(0, len(data) - 1):
            color = "#6a6b6c" if stop_condition[i] else colors[i]

            loc = [
                (data.iloc[i]["lat"], data.iloc[i]["lon"]),
                (data.iloc[i + 1]["lat"], data.iloc[i + 1]["lon"]),
            ]
            folium.PolyLine(
                locations=loc,
                color=color,
                weight=weight,
                opacity=1,
            ).add_to(m)

    else:
        # Create a list of locations and corresponding colors based on speed
        for i in range(len(data) - 1):
            loc = [
                (data.iloc[i]["lat"], data.iloc[i]["lon"]),
                (data.iloc[i + 1]["lat"], data.iloc[i + 1]["lon"]),
            ]

            AntPath(
                locations=loc,
                color=colors[i],
                weight=weight,
                opacity=0.4,
                dash_array=[1, 10],
                delay=delays[i],
                pulse_color=colors[i],
            ).add_to(m)

    return m


# def visualize(data, color_by_speed: bool = False, marker_by_fishing: bool = False):
#     # Create a map centered on the first latitude/longitude position

#     # Add lines connecting each latitude/longitude point

#     # Set the color of the polyline based on speed if requested
#     if color_by_speed:
#         for color, s_min, s_max in speed_ranges:
#             folium.PolyLine(
#             ).add_to(m)
#         folium.PolyLine(
#         ).add_to(m)

#     # Add arrows to indicate the sense of the trajectory
#     for i, row in data.iterrows():
#         if i == 0:

#     # Add markers for each fishing point if requested
#     if marker_by_fishing:
#         for i, row in fishing_points.iterrows():
#             folium.Marker(
#             ).add_to(m)
