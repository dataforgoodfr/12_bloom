import folium
import geopandas as gpd
from geoalchemy2.elements import WKTElement
from geopy import distance
from shapely import wkb
from shapely.geometry import Point, Polygon
from sqlalchemy import func

from bloom.config import settings
from bloom.infra.database.database_manager import Database
from bloom.infra.database.sql_model import MPA


def get_closest_marine_protected_areas(
    coord: tuple[float, float] = (58.373683, -8.080092),
    radius: int = 100,
) -> (list[MPA], gpd.GeoDataFrame):
    ##### CREATE CIRCLE
    db = Database(settings.db_url)

    # Create a Point object
    Point(coord[1], coord[0])

    # Calculate the coordinates of the circle's boundary points
    boundary_points = []
    for bearing in range(0, 360, 60):
        destination = distance.distance(kilometers=radius).destination(coord, bearing)
        boundary_points.append((destination.longitude, destination.latitude))

    # Create a Polygon from the boundary points
    circle = Polygon(boundary_points)

    # Assuming circle is a Shapely Polygon object with coordinates in WGS84 (SRID 4326)
    circle_srid = 4326

    # Convert the Polygon object to a WKT string
    wkt_circle = WKTElement(circle.wkt, srid=circle_srid)

    with db.session() as session:
        mpas = (
            session.query(MPA)
            .filter(func.ST_Intersects(MPA.geometry, wkt_circle))
            .all()
        )
        if mpas:
            print(f"Circle overlaps with the following polygons: {len(mpas)}")
        session.close()

    gdf = convert_list_of_mpas_to_gdf(mpas)

    return mpas, gdf


def add_closest_marine_protected_areas(
    mpas: list[MPA],
    m: folium.Map,
    show_iucn: bool = True,
) -> None:
    for mpa in mpas:
        mpa.add_to_map(m, show_iucn=show_iucn)


def convert_list_of_mpas_to_gdf(mpas: list[MPA]) -> gpd.GeoDataFrame:
    keys = [
        "name",
        "iucn_category",
        "color",
        "protected_area_category",
        "gov_type",
        "type",
        "index",
    ]
    mpas_metadata = [{key: getattr(mpa, key) for key in keys} for mpa in mpas]
    mpas_geometry = [wkb.loads(bytes(mpa.geometry.data)) for mpa in mpas]

    gdf = gpd.GeoDataFrame(mpas_metadata, geometry=mpas_geometry, crs="EPSG:4326")
    return gdf
