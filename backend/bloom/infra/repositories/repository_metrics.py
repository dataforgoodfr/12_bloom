from bloom.domain.metrics import Metrics
from contextlib import AbstractContextManager
from typing import Any, List, Union

import pandas as pd
from dependency_injector.providers import Callable
from sqlalchemy.orm import Session

from bloom.infra.database import sql_model

from sqlalchemy import and_, or_, select, update, text, join




class MetricsRepository:

    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

  #  def get_vessel_excursion_segment_by_id(self, session, segment_id: int) -> pd.DataFrame:
  #      stmt = select(
  #          sql_model.Vessel.id,
  #          sql_model.Vessel.mmsi,
  #          sql_model.Vessel.ship_name
  #          sql_model.Vessel.country_iso3
  #          sql_model.Vessel.imo
  #      ).join(
  #          sql_model.Excursion,
  #          sql_model.Excursion.vessel_id == sql_model.Vessel.id
  #      ).join(
  #          sql_model.Segment,
  #          sql_model.Segment.excursion_id == sql_model.Excursion.id
  #      ).where(
  #          sql_model.Segment.id == segment_id
  #      )
        
  #      result = session.execute(stmt)
  #      if not result:
  #          return None
  #      df = pd.DataFrame(result, columns=["vessel_id", "vessel_mmsi", "ship_name", "vessel_country_iso3","vessel_imo"])
  #      return df

    def batch_create_metrics(
            self, session: Session, metricss: list[Metrics]
    ) -> list[Metrics]:
        orm_list = [MetricsRepository.map_to_orm(metrics) for metrics in metricss]
        session.add_all(orm_list)
        return [MetricsRepository.map_to_domain(orm) for orm in orm_list]


    @staticmethod
    def map_to_orm(metrics: Metrics) -> sql_model.Metrics:
        return sql_model.Metrics(
            timestamp=metrics.timestamp,
            vessel_id=metrics.vessel_id,
            type=metrics.type,
            vessel_mmsi=metrics.vessel_mmsi,
            ship_name=metrics.ship_name,
            vessel_country_iso3=metrics.vessel_country_iso3,
            vessel_imo=metrics.vessel_imo,
            duration_total=metrics.duration_total,
            duration_fishing=metrics.duration_fishing,
            zone_name=metrics.zone_name,
            zone_id=metrics.zone_id,
            zone_category=metrics.zone_category,
            zone_sub_category=metrics.zone_sub_category,
        )            


    @staticmethod
    def map_to_domain(metrics: sql_model.Metrics) -> Metrics:
            return Metrics(
                timestamp=metrics.timestamp,
                vessel_id=metrics.vessel_id,
                type=metrics.type,
                vessel_mmsi=metrics.vessel_mmsi,
                ship_name=metrics.ship_name,
                vessel_country_iso3=metrics.vessel_country_iso3,
                vessel_imo=metrics.vessel_imo,
                duration_total=metrics.duration_total,
                duration_fishing=metrics.duration_fishing,
                zone_name=metrics.zone_name,
                zone_id=metrics.zone_id,
                zone_category=metrics.zone_category,
                zone_sub_category=metrics.zone_sub_category,
            )            





