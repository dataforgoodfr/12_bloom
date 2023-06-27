from contextlib import AbstractContextManager
from datetime import datetime

from dependency_injector.providers import Callable
from sqlalchemy.sql import text

from bloom.domain.alert import Alert


class RepositoryVessel:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def save_alerts(self, timestamp: datetime) -> None:
        with self.session_factory() as session:

            sql = text(
                f"""
                    INSERT INTO alert(timestamp,vessel_id,mpa_id)
                    (SELECT spire_vessel_positions.timestamp,
                                spire_vessel_positions.vessel_id,mpa.index
                        FROM spire_vessel_positions
                        JOIN mpa
                        ON ST_Contains(mpa.geometry, spire_vessel_positions.position)
                        WHERE spire_vessel_positions.timestamp = '{timestamp}');
                    """,  # nosec
            )
            session.execute(sql)

    def load_alert(self, timestamp: datetime) -> list[Alert]:
        with self.session_factory() as session:
            # requesting the polygons was too long
            sql = text(
                f"""
                    SELECT timestamp, ship_name, mmsi, lp_time, position,
                            mpa."NAME", mpa."IUCN_CAT"
                    FROM (SELECT a.mpa_id as mpa_id, a.timestamp as timestamp,
                            spire.ship_name as ship_name,
                            spire.mmsi as mmsi, spire.last_position_time as lp_time,
                            ST_AsText(spire.position) as position
                        FROM alert a
                        JOIN (SELECT * FROM spire_vessel_positions
                        WHERE spire_vessel_positions.timestamp = '{timestamp}') as spire
                        ON a.vessel_id = spire.vessel_id
                        WHERE  a.timestamp = '{timestamp}') as habile
                        JOIN mpa ON mpa_id = mpa.index
                    """,  # nosec
            )
            e = session.execute(sql)
            if not e:
                return []
            print(e)
            return None  # [self.map_sql_to_alert(vessel) for vessel in e]
