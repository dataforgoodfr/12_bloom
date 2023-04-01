from pathlib import Path

from geopandas import GeoDataFrame, GeoSeries
from shapely import Point, Polygon

from bloom.domain.polygon import AbstractPolygon


class PolygonFileRepository(AbstractPolygon):
    def __init__(self) -> None:
        # Rendre relatif
        self.polygons_path = Path.joinpath(Path.cwd(), "data/my_file.geojson")
        self.polygons: GeoSeries = GeoSeries()

    def load_polygons(self) -> list[Polygon]:
        polygons = GeoDataFrame.from_file(self.polygons_path.__str__())
        self.polygons = polygons.geometry
        return polygons

    def is_point_in_polygons(self, point: Point) -> Polygon | bool:
        if len(self.polygons[self.polygons.contains(point)]) > 0:
            return self.polygons[self.polygons.contains(point)][0]
        return False
