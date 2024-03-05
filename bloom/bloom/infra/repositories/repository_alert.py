from contextlib import AbstractContextManager
from datetime import datetime

import sqlalchemy
from dependency_injector.providers import Callable
from sqlalchemy.sql import text

from bloom.domain.alert import Alert


class RepositoryAlert:
    def __init__(
        self,
        session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def save_alerts(self, timestamp: datetime) -> None:
        with self.session_factory() as session:
            sql = text(
                f"""
                    INSERT INTO alert(timestamp,vessel_id,cross_mpa,mpa_ids)
                    (
                        SELECT timestamp, vessel_id, (CAST(ST_Contains(mpa_fr_with_mn.geometry,current_position) AS INT) - CAST(ST_Contains(mpa_fr_with_mn.geometry,previous_position) AS INT)) as cross_mpa, ARRAY_AGG(mpa_fr_with_mn.index ORDER BY mpa_fr_with_mn.index DESC) AS mpa_ids FROM 
                            (SELECT spire_vessel_positions.vessel_id AS vessel_id,
                                    spire_vessel_positions.position AS current_position,
                                    spire_vessel_positions.timestamp AS timestamp,
                                    LAG(spire_vessel_positions.position) OVER (PARTITION BY spire_vessel_positions.vessel_id ORDER BY spire_vessel_positions.timestamp) AS previous_position
                                FROM spire_vessel_positions WHERE spire_vessel_positions.timestamp >= TIMESTAMP '{timestamp}' - INTERVAL '15 minutes' AND spire_vessel_positions.timestamp < TIMESTAMP '{timestamp}' + INTERVAL '15 minutes' ) AS foo
                            CROSS JOIN mpa_fr_with_mn WHERE previous_position IS NOT NULL and ST_Contains(mpa_fr_with_mn.geometry,current_position) != ST_Contains(mpa_fr_with_mn.geometry,previous_position) GROUP BY vessel_id, timestamp,cross_mpa
                    );
                    """,  # nosec: B608  # noqa: E501
            )
            session.execute(sql)
            session.commit()
            return
        
    # an other query with the same result :
    # WITH cte_query1 AS (
    #    SELECT spire_vessel_positions.vessel_id AS vessel_id, ARRAY_AGG(mpa_fr_with_mn.index ORDER BY mpa_fr_with_mn.index DESC) AS mpa_ids            # noqa: E501
    #    FROM spire_vessel_positions 
    #    JOIN mpa_fr_with_mn ON ST_Contains(mpa_fr_with_mn.geometry, spire_vessel_positions.position)                                                   # noqa: E501
    #    WHERE spire_vessel_positions.timestamp = TO_TIMESTAMP('2023-11-17 12:00', 'YYYY-MM-DD HH24:MI')                                                # noqa: E501
    #    GROUP BY vessel_id
    #    ),
    #    cte_query2 AS (
    #    SELECT DISTINCT spire_vessel_positions.vessel_id AS vessel_id, ARRAY_AGG(mpa_fr_with_mn.index ORDER BY mpa_fr_with_mn.index DESC) AS mpa_ids   # noqa: E501
    #    FROM spire_vessel_positions 
    #    JOIN mpa_fr_with_mn ON ST_Contains(mpa_fr_with_mn.geometry, spire_vessel_positions.position)                                                   # noqa: E501
    #    WHERE spire_vessel_positions.timestamp = TO_TIMESTAMP('2023-11-17 12:15', 'YYYY-MM-DD HH24:MI')                                                # noqa: E501
    #    GROUP BY vessel_id
    #    )
    #    SELECT vessel_id, mpa_ids, -1 AS value FROM cte_query1 EXCEPT SELECT vessel_id, mpa_ids, -1 AS value FROM cte_query2                           # noqa: E501
    #    UNION ALL
    #    SELECT vessel_id, mpa_ids, 1 AS value FROM cte_query2 EXCEPT SELECT vessel_id, mpa_ids, 1 AS value FROM cte_query1                             # noqa: E501

    def load_alert(self, timestamp: datetime) -> list[Alert]:
        with self.session_factory() as session:
            # requesting the polygons was too long.
            # If the join become too long,we can create an alert table with all the data
            # In this case domain will be equal to  sql model
            sql = text(
                f"""
                    SELECT timestamp, ship_name, mmsi, lp_time, position,
                           mpa_fr_with_mn.name, mpa_fr_with_mn."IUCN_CAT"
                    FROM (SELECT a.mpa_ids as mpa_ids, a.timestamp as timestamp,
                            spire.ship_name as ship_name,
                            spire.mmsi as mmsi, spire.last_position_time as lp_time,
                            ST_AsText(spire.position) as position
                        FROM alert a
                        JOIN (SELECT * FROM spire_vessel_positions
                        WHERE spire_vessel_positions.timestamp = '{timestamp}') as spire
                        ON a.vessel_id = spire.vessel_id
                        WHERE  a.timestamp = '{timestamp}' and cross_mpa = 1) as habile
                        JOIN mpa_fr_with_mn ON mpa_ids[1] = mpa_fr_with_mn.index
                    """,  # nosec: B608
            )
            e = session.execute(sql)
            if not e:
                return []
            return [self.map_sql_to_alert(row) for row in e]

    def map_sql_to_alert(self, row: sqlalchemy.engine.row.Row) -> Alert:
        return Alert(
            ship_name=row[1],
            mmsi=row[2],
            last_position_time=row[3],
            position=row[4],
            iucn_cat=row[6],
            mpa_name=row[5],
        )
