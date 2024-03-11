"""
- Clean "UN/LOCODE" column in wpi.csv and rename it to "locode"
- Join ports.csv with the WPI (World Port Index) data on the "locode" column (if a row in ports.csv has a no "locode" in the WPI data, it should be discarded)
- Filter the resulting dataframe to keep only big ports

Tidal Range (m): Les ports avec une grande amplitude de marée peuvent généralement accueillir de gros navires et sont souvent des ports importants.
Entrance Width (m): Une large entrée permet l'accès de grands navires.
Channel Depth (m): Une profondeur de chenal importante est nécessaire pour les grands navires à fort tirant d'eau.
Anchorage Depth (m): La profondeur à l'ancre indique si de grands navires peuvent mouiller en toute sécurité.
Cargo Pier Depth (m): La profondeur au quai de chargement est critique pour accueillir de grands navires de fret.
Oil Terminal Depth (m), Liquified Natural Gas Terminal Depth (m): La profondeur des terminaux pétroliers et gaziers indique la capacité du port à accueillir des pétroliers et des méthaniers, qui sont souvent de très grands navires.
Maximum Vessel Length (m), Maximum Vessel Beam (m), Maximum Vessel Draft (m): Ces mesures donnent une idée de la taille maximale des navires que le port peut accueillir.
Harbor Size: La taille du port peut indiquer sa capacité globale.
"""

import os
import pandas as pd

csv_input1 = os.path.join(os.path.dirname(__file__), "../ports_rad3000_res10.csv")
csv_input2 = os.path.join(os.path.dirname(__file__), "../wpi.csv")
csv_output = os.path.join(os.path.dirname(__file__), f"../result.csv")

df_ports = pd.read_csv(csv_input1, sep=";")
df_wpi = pd.read_csv(csv_input2, sep=";")

# rename "UN/LOCODE" to "locode"
df_wpi.rename(columns={"UN/LOCODE": "locode"}, inplace=True)

# drop rows with no "locode"
df_wpi = df_wpi.dropna(subset=["locode"])

#c lean "locode" column
df_wpi["locode"] = df_wpi["locode"].apply(lambda x: x.replace(" ", ""))

# join
print(df_ports.shape)
df = pd.merge(df_ports, df_wpi, on="locode", how="inner")
print(df.shape)

# filter
# on anchor depth
# depth = 1
# print(f"Before filter on depth = {depth}, shape = {df.shape}")
# df = df[df["Anchorage Depth (m)"] > depth]
# print(f"After filter on depth = {depth}, shape = {df.shape}")

# just keep columns for db
# url;country;port;locode;latitude;longitude;geometry_point;geometry_buffer
columns = ["url", "country", "port", "locode", "latitude", "longitude", "geometry_point", "geometry_buffer"]
df = df[columns]

# save
df.to_csv(csv_output, sep=";", index=False)
       