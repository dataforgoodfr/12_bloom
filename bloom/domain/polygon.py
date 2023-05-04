from abc import ABC, abstractmethod

from shapely.geometry import Point, Polygon


class AbstractPolygon(ABC):
    @abstractmethod
    def load_polygons(self) -> list[Polygon]:
        raise NotImplementedError

    @abstractmethod
    def is_point_in_polygons(self, point: Point) -> bool:
        raise NotImplementedError
