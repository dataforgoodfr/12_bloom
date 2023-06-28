from contextlib import AbstractContextManager

from dependency_injector.providers import Callable
from shapely import Point
from sqlalchemy.sql import text

from bloom.config import settings


class RepositoryRaster:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def select_distance_shore(self, point: Point) -> int:
        with self.session_factory() as session:
            sql = text(
                f"""
    SELECT ST_Value(rast, ST_SetSRID(ST_MakePoint({point.x},{point.y}),{settings.srid}))
    AS val FROM distance_shore WHERE
    ST_Intersects(rast, ST_SetSRID(ST_MakePoint({point.x},{point.y}),{settings.srid}));
                    """,  # nosec: B608
            )
            e = session.execute(sql)
            return e.first()[0]

    def select_distance_port(self, point: Point) -> int:
        with self.session_factory() as session:
            sql = text(
                f"""
    SELECT ST_Value(rast, ST_SetSRID(ST_MakePoint({point.x},{point.y}),{settings.srid}))
    AS val FROM distance_port WHERE
    ST_Intersects(rast, ST_SetSRID(ST_MakePoint({point.x},{point.y}),{settings.srid}));
                    """,  # nosec: B608
            )
            e = session.execute(sql)
            return e.first()[0]
