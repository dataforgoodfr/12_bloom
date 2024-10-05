from fastapi import APIRouter, Depends, Query
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from bloom.infra.database import sql_model
from bloom.domain.segment import Segment
from bloom.infra.repositories.repository_segment import SegmentRepository
import json
from pydantic import BaseModel, ConfigDict

router = APIRouter()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)


class ResponseMetricsVesselInActiviySchema(BaseModel):
    id: int
    mmsi: int
    ship_name: str
    width: Optional[float] = None
    length: Optional[float] = None
    country_iso3: Optional[str] = None
    type: Optional[str] = None
    imo: Optional[int] = None
    cfr: Optional[str] = None
    external_marking: Optional[str] = None
    ircs: Optional[str] = None
    home_port_id: Optional[int] = None
    details: Optional[str] = None
    tracking_activated: Optional[bool]
    tracking_status: Optional[str]
    length_class: Optional[str]
    check: Optional[str]
    total_time_at_sea: timedelta

@router.get("/metrics/vessels-in-activity",
            response_model=list[ResponseMetricsVesselInActiviySchema],
            tags=['metrics'])
def read_metrics_vessels_in_activity_total(start_at: datetime,
                                           end_at: datetime = datetime.now(),
                                           limit: int = None,
                                           order_by: str = 'DESC'
                                           ):
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt=select(sql_model.Vessel.id,
                    sql_model.Vessel.mmsi,
                    sql_model.Vessel.ship_name,
                    sql_model.Vessel.width,
                    sql_model.Vessel.length,
                    sql_model.Vessel.country_iso3,
                    sql_model.Vessel.type,
                    sql_model.Vessel.imo,
                    sql_model.Vessel.cfr,
                    sql_model.Vessel.external_marking,
                    sql_model.Vessel.ircs,
                    sql_model.Vessel.home_port_id,
                    sql_model.Vessel.details,
                    sql_model.Vessel.tracking_activated,
                    sql_model.Vessel.tracking_status,
                    sql_model.Vessel.length_class,
                    sql_model.Vessel.check,
                    func.sum(sql_model.Excursion.total_time_at_sea).label("total_time_at_sea")
                    )\
            .select_from(sql_model.Segment)\
            .join(sql_model.Excursion, sql_model.Segment.excursion_id == sql_model.Excursion.id)\
            .join(sql_model.Vessel, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
            .where(
                or_(
                    sql_model.Excursion.arrival_at.between(start_at,end_at),
                    and_(sql_model.Excursion.departure_at <= end_at,
                         sql_model.Excursion.arrival_at == None))
            )\
            .group_by(sql_model.Vessel.id,sql_model.Excursion.total_time_at_sea)
        stmt = stmt.limit(limit) if limit != None else stmt
            
        stmt =  stmt.order_by(sql_model.Excursion.total_time_at_sea.asc())\
                if  order_by.upper() == 'ASC' \
                else stmt.order_by(sql_model.Excursion.total_time_at_sea.desc())        
        return  session.execute(stmt).all()

@router.get("/metrics/zone-visited",
            tags=['metrics'] )
def read_metrics_vessels_in_activity_total(start_at: datetime,
                                           end_at: datetime = None,
                                           limit: int = None,
                                           order_by: str = 'DESC'):
    pass

@router.get("/metrics/vessels/{vessel_id}/visits/{visit_type}", tags=['metrics'])
def read_metrics_vessels_visits_by_visit_type(
        vessel_id: int,
        visit_type: str,
        start_at: datetime,
        end_at: datetime = None,
        limit: int = 10,
        orderBy: str = 'DESC'):
    pass