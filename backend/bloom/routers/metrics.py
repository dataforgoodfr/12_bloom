from fastapi import APIRouter, Depends, Query, Body,Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from bloom.infra.database import sql_model
from bloom.infra.repositories.repository_segment import SegmentRepository
import json
from bloom.domain.metrics import (ResponseMetricsVesselInActiviySchema,
                                 ResponseMetricsZoneVisitedSchema,
                                 ResponseMetricsZoneVisitingTimeByVesselSchema)
from bloom.domain.api import (  DatetimeRangeRequest,
                                PaginatedRequest,OrderByRequest,OrderByEnum,
                                paginate,PagedResponseSchema,PageParams,
                                X_API_KEY_HEADER)

router = APIRouter()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)




@router.get("/metrics/vessels-in-activity",
            response_model=list[ResponseMetricsVesselInActiviySchema],
            tags=['metrics'])
def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           #pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           auth: str = Depends(X_API_KEY_HEADER),
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
                    sql_model.Excursion.arrival_at.between(datetime_range.start_at,datetime_range.end_at),
                    and_(sql_model.Excursion.departure_at <= datetime_range.end_at,
                         sql_model.Excursion.arrival_at == None))
            )\
            .group_by(sql_model.Vessel.id,sql_model.Excursion.total_time_at_sea)
        #stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            
        stmt =  stmt.order_by(sql_model.Excursion.total_time_at_sea.asc())\
                if  order.order == OrderByEnum.ascending \
                else stmt.order_by(sql_model.Excursion.total_time_at_sea.desc())        
        return  session.execute(stmt).all()

@router.get("/metrics/zone-visited",
            response_model=list[ResponseMetricsZoneVisitedSchema],
            tags=['metrics'] )
def read_metrics_vessels_in_activity_total(datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PaginatedRequest = Depends(),
                                           auth: str = Depends(X_API_KEY_HEADER),):
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt=select(
            sql_model.Zone.id.label("zone_id"),
            sql_model.Zone.category.label("zone_category"),
            sql_model.Zone.sub_category.label("zone_sub_category"),
            sql_model.Zone.name.label("zone_name"),
            func.sum(sql_model.Segment.segment_duration).label("visiting_duration")
            )\
            .where(
                or_(
                    sql_model.Segment.timestamp_start.between(datetime_range.start_at,datetime_range.end_at),
                    sql_model.Segment.timestamp_end.between(datetime_range.start_at,datetime_range.end_at),)
            )\
            .group_by(sql_model.Zone.id)
        stmt = stmt.limit(limit) if limit != None else stmt
        stmt =  stmt.order_by("visiting_duration")\
                if  pagination.order_by == OrderByRequest.ascending \
                else stmt.order_by("visiting_duration") 
        return  session.execute(stmt).all()

@router.get("/metrics/zones/{zone_id}/visiting-time-by-vessel",
            response_model=list[ResponseMetricsZoneVisitingTimeByVesselSchema],
            tags=['metrics'])
def read_metrics_zone_visiting_time_by_vessel(
                    datetime_range: Annotated[DatetimeRangeRequest,Body()],
                    zone_id: int,
                    limit: int = None,
                    order_by: str = 'DESC',
                    auth: str = Depends(X_API_KEY_HEADER),):
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt=select(
            sql_model.Zone.id.label("zone_id"),
            sql_model.Zone.category.label("zone_category"),
            sql_model.Zone.sub_category.label("zone_sub_category"),
            sql_model.Zone.name.label("zone_name"),
            sql_model.Vessel.id.label("vessel_id"),
            sql_model.Vessel.ship_name.label("vessel_name"),
            sql_model.Vessel.type.label("vessel_type"),
            sql_model.Vessel.length_class.label("vessel_length_class"),
            func.sum(sql_model.Segment.segment_duration).label("zone_visiting_time_by_vessel")
        )\
        .select_from(sql_model.Zone)\
        .join(sql_model.RelSegmentZone, sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
        .join(sql_model.Segment, sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
        .join(sql_model.Excursion, sql_model.Excursion.id == sql_model.Segment.excursion_id)\
        .join(sql_model.Vessel, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
        .where(sql_model.Zone.id == zone_id)\
        .group_by(sql_model.Zone.id,sql_model.Vessel.id)
        return  session.execute(stmt).all()



@router.get("/metrics/vessels/{vessel_id}/visits/{visit_type}", tags=['metrics'])
def read_metrics_vessels_visits_by_visit_type(
        vessel_id: int,
        visit_type: str,
        datetime_range: DatetimeRangeRequest = Depends(),
        pagination: PaginatedRequest = Depends(),
        auth: str = Depends(X_API_KEY_HEADER),):
    pass