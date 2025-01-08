from typing import List
import pandas as pd
import geopandas as gpd

from bloom.container import UseCases
from bloom.config import settings

def find_positions_in_port_buffer(vessel_positions: List[tuple]) -> List[tuple]:
    """Assigns vessel positions to their port if any. If a vessel is not in a port,
    assign np.nan as port_id

    :param List[tuple] vessel_positions: fields "vessel_id", "longitude", "latitude", 

    :return List[tuple] vessel_positions: fields "vessel_id", "longitude", "latitude", "port_name", "port_id"
        if a vessel is not in a port, "port_id" is np.nan
    """

    # Convert vessel positions into a GeoDataFrame
    df_vessel_positions = pd.DataFrame(
        vessel_positions, columns=["vessel_id", "lon", "lat"]
    )
    gdf_vessel_positions = gpd.GeoDataFrame(
        df_vessel_positions,
        geometry=gpd.points_from_xy(
            df_vessel_positions["lon"], df_vessel_positions["lat"]
        ),
        crs=settings.srid,
    )

    # Get all ports from DataBase
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        port_repository = use_cases.port_repository(session)
        ports = port_repository.list()
        
    df_ports = pd.DataFrame(
        [[p.id, p.name, p.geometry_buffer] for p in ports],
        columns=["port_id", "port_name", "geometry"],
    )
    gdf_ports = gpd.GeoDataFrame(df_ports, geometry="geometry", crs=settings.srid)

    # Spatial join to match vessel positions to ports polygons
    gdf_vessel_positions = gdf_vessel_positions.sjoin(gdf_ports, how="left")

    # Format response as list of tuples with port_id as last element
    response = list(
        zip(
            gdf_vessel_positions["vessel_id"],
            gdf_vessel_positions["lon"],
            gdf_vessel_positions["lat"],
            gdf_vessel_positions["port_id"],
            gdf_vessel_positions["port_name"],
        )
    )

    return response