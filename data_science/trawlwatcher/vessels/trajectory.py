

import folium
from datetime import datetime
import pandas as pd
from folium import plugins
from folium.plugins import AntPath
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from shapely.geometry import LineString

def visualize(data,color_by_speed: bool = False, marker_by_fishing: bool = False,with_animation = True,min_speed = 2.0,max_speed = None,weight = 5,cmap=plt.cm.Spectral_r):
    # Create a map centered on the first latitude/longitude position
    map_center = [data.iloc[0]['lat'], data.iloc[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=6)

    # Add markers for the first and last points
    folium.Marker(location=[data.iloc[0]['lat'], data.iloc[0]['lon']], icon=folium.Icon(icon='play', color='blue',prefix = "fa")).add_to(m)
    folium.Marker(location=[data.iloc[-1]['lat'], data.iloc[-1]['lon']], icon=folium.Icon(icon='stop', color='red')).add_to(m)

    # Add markers for each data point only when the boat is fishing
    if marker_by_fishing:
        for i, row in data.iterrows():
            if row['is_fishing'] > 0:
                folium.Marker(location=[row['lat'], row['lon']], icon=folium.Icon(icon='fish', color='blue',prefix = "fa")).add_to(m)

    # Define a function to color the polyline based on speed
    def speed_color(speed, cmap = cmap):
        rgba = cmap(speed)
        return mcolors.rgb2hex(rgba)

    def antpath_delay(speed, max_speed = 30, min_delay=1000, max_delay=20000):
        return min_delay + (1 - speed) * (max_delay - min_delay)

    if max_speed is None:
        max_speed = data["speed"].max()

    speeds = data["speed"].clip(min_speed,max_speed)
    normalized_speeds = (speeds - min_speed) / (max_speed - min_speed)
    colors = normalized_speeds.map(speed_color).tolist()
    delays = normalized_speeds.map(antpath_delay).tolist()


    if not with_animation:

        # Add lines connecting each latitude/longitude point with a color based on speed
        for i in range(0, len(data)-1):

            loc = [(data.iloc[i]['lat'], data.iloc[i]['lon']), (data.iloc[i+1]['lat'], data.iloc[i+1]['lon'])]
            folium.PolyLine(
                locations=loc,
                color=colors[i],
                weight=weight,
                opacity=1
            ).add_to(m)
    
    else:
            
        # Create a list of locations and corresponding colors based on speed
        for i in range(len(data) - 1):
            loc = [(data.iloc[i]['lat'], data.iloc[i]['lon']), (data.iloc[i+1]['lat'], data.iloc[i+1]['lon'])]

            AntPath(
                locations=loc,
                color=colors[i],
                weight=weight,
                opacity=0.4,
                dash_array=[1, 10],
                delay=delays[i],
                pulse_color=colors[i]
            ).add_to(m)

    return m


# def visualize(data, color_by_speed: bool = False, marker_by_fishing: bool = False):
#     # Create a map centered on the first latitude/longitude position
#     map_center = [data.iloc[0]['lat'], data.iloc[0]['lon']]
#     m = folium.Map(location=map_center, zoom_start=12)

#     # Add lines connecting each latitude/longitude point
#     locations = data[['lat', 'lon']].values.tolist()

#     # Set the color of the polyline based on speed if requested
#     if color_by_speed:
#         speed_colors = [
#             ('blue', 0, 3),
#             ('green', 3, 7),
#             ('orange', 7, 10),
#             ('red', 10, 100)
#         ]
#         speed_ranges = [(c, s_min, s_max) for c, s_min, s_max in speed_colors]
#         speed = data['speed']
#         for color, s_min, s_max in speed_ranges:
#             locations_subset = [locations[i] for i in range(len(speed)) if s_min <= speed[i] < s_max]
#             folium.PolyLine(
#                 locations=locations_subset,
#                 color=color,
#                 weight=3,
#                 opacity=0.7
#             ).add_to(m)
#     else:
#         folium.PolyLine(
#             locations=locations,
#             color='blue',
#             weight=3,
#             opacity=0.7
#         ).add_to(m)

#     # Add arrows to indicate the sense of the trajectory
#     for i, row in data.iterrows():
#         if i == 0:
#             continue
#         start_location = [data.iloc[i - 1]['lat'], data.iloc[i - 1]['lon']]
#         end_location = [row['lat'], row['lon']]
#         arrow = folium.plugins.AntPath(locations=[start_location, end_location], color='grey')
#         arrow.add_to(m)

#     # Add markers for each fishing point if requested
#     if marker_by_fishing:
#         fishing_points = data[data['is_fishing'] > 0]
#         for i, row in fishing_points.iterrows():
#             folium.Marker(
#                 location=[row['lat'], row['lon']],
#                 icon=folium.Icon(icon='fish', color='red')
#             ).add_to(m)

#     return m

