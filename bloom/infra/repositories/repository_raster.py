from contextlib import AbstractContextManager

from dependency_injector.providers import Callable
from sqlalchemy import func

from bloom.infra.database import sql_model


class RepositoryVessel:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def select_distance_shore(self) -> int:
        with self.session_factory() as session:
            e = session.query(sql_model.DistanceShore).filter(
                func.ST_Contains(sql_model.DistanceShore, "POINT(1.83 51.18)"),
            )

            if not e:
                return []
            print(e)
            return None
