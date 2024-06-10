from time import perf_counter

import geopandas as gpd
import pandas as pd
import pyproj
import shapely
from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.logger import logger
from scipy.spatial import Voronoi
from shapely.geometry import LineString, Polygon
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from datetime import datetime, timezone

radius_m = 3000  # Radius in meters
resolution = 10  # Number of points in the resulting polygon


# Function to create geodesic buffer around a point
def geodesic_point_buffer(lat: float, lon: float, radius_m: int, resolution: int) -> Polygon:
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


def assign_voronoi_buffer(ports: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Computes a buffer around each port such as buffers do not overlap each other

    :param gpd.GeoDataFrame ports: fields "id", "latitude", "longitude", "geometry_point"
        from the table "dim_ports"
    :return gpd.GeoDataFrame: same as input but field "geometry_point" is replaced
        by "geometry_buffer"
    """
    # Convert to CRS 6933 to write distances as meters (instead of degrees)
    ports.to_crs(6933, inplace=True)

    # Create an 8km buffer around each port
    # FIXME: maybe put the buffer distance as a global parameter
    ports["buffer"] = ports["geometry_point"].apply(lambda p: shapely.buffer(p, 8000))

    # Convert points back to CRS 4326 (lat/lon) --> buffers are still expressed in 6933
    ports.to_crs(settings.srid, inplace=True)

    # Convert buffers to 4326
    ports = gpd.GeoDataFrame(ports, geometry="buffer", crs=6933).to_crs(settings.srid)

    # Create Voronoi polygons, i.e. match each port to the area which is closest to this port
    vor = Voronoi(list(zip(ports.longitude, ports.latitude)))
    lines = []
    for line in vor.ridge_vertices:
        if -1 not in line:
            lines.append(LineString(vor.vertices[line]))
        else:
            lines.append(LineString())
    vor_polys = [poly for poly in shapely.ops.polygonize(lines)]

    # Match each port to its Voronoi polygon
    vor_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(vor_polys), crs=4326)
    vor_gdf["voronoi_poly"] = vor_gdf["geometry"].copy()
    ports = gpd.GeoDataFrame(ports, geometry="geometry_point", crs=4326)
    vor_ports = ports.sjoin(vor_gdf, how="left").drop(columns=["index_right"])

    # Corner case: ports at extremes latitude and longitude have no Voroni polygon
    # (15 / >5800) cases --> duplicate regular buffer instead
    vor_ports.loc[vor_ports.voronoi_poly.isna(), "voronoi_poly"] = vor_ports.loc[
        vor_ports.voronoi_poly.isna(), "buffer"
    ]

    # Get intersection between fixed-size buffer and Voronoi polygon to get final buffer
    vor_ports["geometry_buffer"] = vor_ports.apply(
        lambda row: shapely.intersection(row["buffer"], row["voronoi_poly"]),
        axis=1
    )
    vor_ports["buffer_voronoi"] = vor_ports["geometry_buffer"].copy()
    vor_ports = gpd.GeoDataFrame(vor_ports, geometry="geometry_buffer", crs=4326)
    vor_ports = vor_ports[["id", "latitude", "longitude", "geometry_buffer"]].copy()

    return vor_ports


def run() -> None:
    use_cases = UseCasesContainer()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    items = []
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(session, "compute_port_geometry_buffer")
        logger.info(f"Point in time={point_in_time}")
        now = datetime.now(timezone.utc)
        ports = port_repository.get_ports_updated_created_after(session, point_in_time)
        if ports:
            df = pd.DataFrame(
                [[p.id, p.geometry_point, p.latitude, p.longitude] for p in ports],
                columns=["id", "geometry_point", "latitude", "longitude"],
            )
            gdf = gpd.GeoDataFrame(df, geometry="geometry_point", crs=settings.srid)

            # Apply the buffer function to create buffers
            gdf = assign_voronoi_buffer(gdf)

            for row in gdf.itertuples():
                items.append({"id": row.id, "geometry_buffer": row.geometry_buffer})
            port_repository.batch_update_geometry_buffer(session, items)
        TaskExecutionRepository.set_point_in_time(session, "compute_port_geometry_buffer", now)
        session.commit()
    logger.info(f"{len(items)} buffer de ports mis à jour")


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Calcul des buffer de ports")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Calcul des buffer de ports en {duration:.2f}s")
