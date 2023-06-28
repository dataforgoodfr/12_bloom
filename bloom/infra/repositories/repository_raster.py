from contextlib import AbstractContextManager

from dependency_injector.providers import Callable
from sqlalchemy import func

from bloom.infra.database import sql_model
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

class RepositoryRaster:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def select_distance_shore(self) -> int:
        with self.session_factory() as session:
            e = session.query(sql_model.DistanceShore.raster).filter(
                func.ST_Intersects(sql_model.DistanceShore.raster, func.ST_SetSRID(func.ST_MakePoint(1.83,51.18),4326)),
            )
            if not e:
                return []
            return e
