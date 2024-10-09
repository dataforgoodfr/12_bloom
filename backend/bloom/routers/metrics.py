from fastapi import APIRouter, Depends, Query, Body,Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, text, literal_column, Row
from bloom.infra.database import sql_model
from bloom.infra.repositories.repository_segment import SegmentRepository
from sqlalchemy.ext.serializer import loads,dumps
import json
import time
from bloom.infra.database.database_manager import Base
from bloom.domain.metrics import (ResponseMetricsVesselInActivitySchema,
                                 ResponseMetricsZoneVisitedSchema,
                                 ResponseMetricsZoneVisitingTimeByVesselSchema,
                                 ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema)
from bloom.dependencies import (  DatetimeRangeRequest,
                                PaginatedRequest,OrderByRequest,OrderByEnum,
                                paginate,PagedResponseSchema,PageParams,
                                X_API_KEY_HEADER, check_apikey,CachedRequest)

from bloom.domain.metrics import TotalTimeActivityTypeRequest

router = APIRouter()
rd = Redis(host=settings.redis_host, port=settings.redis_port, db=0)

@router.get("/metrics/vessels-in-activity",
            response_model=list[ResponseMetricsVesselInActivitySchema],
            tags=['Metrics'])
def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    cache_key=f"{request.url.path}?{request.query_params}"
    cache_payload= rd.get(cache_key)
    start = time.time()
    payload = []
    if cache_payload and not caching.nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=loads(cache_payload)
    else:
        with db.session() as session:
            stmt=select(sql_model.Vessel.id.label("vessel_id"),
                        sql_model.Vessel.mmsi.label("vessel_mmsi"),
                        sql_model.Vessel.ship_name.label("vessel_ship_name"),
                        sql_model.Vessel.width.label("vessel_width"),
                        sql_model.Vessel.length.label("vessel_length"),
                        sql_model.Vessel.country_iso3.label("vessel_country_iso3"),
                        sql_model.Vessel.type.label("vessel_type"),
                        sql_model.Vessel.imo.label("vessel_imo"),
                        sql_model.Vessel.cfr.label("vessel_cfr"),
                        sql_model.Vessel.external_marking.label("vessel_external_marking"),
                        sql_model.Vessel.ircs.label("vessel_ircs"),
                        sql_model.Vessel.home_port_id.label("vessel_home_port_id"),
                        sql_model.Vessel.details.label("vessel_details"),
                        sql_model.Vessel.tracking_activated.label("vessel_tracking_activated"),
                        sql_model.Vessel.tracking_status.label("vessel_tracking_status"),
                        sql_model.Vessel.length_class.label("vessel_length_class"),
                        sql_model.Vessel.check.label("vessel_check"),
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
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt =  stmt.order_by(sql_model.Excursion.total_time_at_sea.asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(sql_model.Excursion.total_time_at_sea.desc())
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()
            serialized=dumps(payload)
            rd.set(cache_key, serialized)
            rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload

@router.get("/metrics/zone-visited",
            response_model=list[ResponseMetricsZoneVisitedSchema],
            tags=['Metrics'] )
def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    cache_key=f"{request.url.path}?{request.query_params}"
    cache_payload= rd.get(cache_key)
    start = time.time()
    payload=[]
    if cache_payload and not caching.nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=loads(cache_payload)
    else:
        use_cases = UseCases()
        payload = []
        db = use_cases.db()
        with db.session() as session:
            stmt=select(
                sql_model.Zone.id.label("zone_id"),
                sql_model.Zone.category.label("zone_category"),
                sql_model.Zone.sub_category.label("zone_sub_category"),
                sql_model.Zone.name.label("zone_name"),
                func.sum(sql_model.Segment.segment_duration).label("visiting_duration")
                )\
                .select_from(sql_model.Zone)\
                .join(sql_model.RelSegmentZone,sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
                .join(sql_model.Segment,sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
                .where(
                    or_(
                        sql_model.Segment.timestamp_start.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Segment.timestamp_end.between(datetime_range.start_at,datetime_range.end_at),)
                )\
                .group_by(sql_model.Zone.id)
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            print(stmt)
            payload=session.execute(stmt).all()
            serialized=dumps(payload)
            rd.set(cache_key, serialized)
            rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload

@router.get("/metrics/zones/{zone_id}/visiting-time-by-vessel",
            response_model=list[ResponseMetricsZoneVisitingTimeByVesselSchema],
            tags=['Metrics'])
def read_metrics_zone_visiting_time_by_vessel(request: Request,
                                            zone_id: int,
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            pagination: PageParams = Depends(),
                                            order: OrderByRequest = Depends(),
                                            caching: CachedRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    cache_key=f"{request.url.path}?{request.query_params}"
    cache_payload= rd.get(cache_key)
    start = time.time()
    payload=[]
    if cache_payload and not caching.nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=loads(cache_payload)
    else:
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
            .where(
                and_(sql_model.Zone.id == zone_id,
                    or_(
                        sql_model.Segment.timestamp_start.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Segment.timestamp_end.between(datetime_range.start_at,datetime_range.end_at),))
                )\
            .group_by(sql_model.Zone.id,sql_model.Vessel.id)
            
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt

            payload=session.execute(stmt).all()
            serialized=dumps(payload)
            rd.set(cache_key, serialized)
            rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload


@router.get("/metrics/vessels/{vessel_id}/activity/{activity_type}",
            response_model=ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema,
            tags=['Metrics'])
def read_metrics_vessels_visits_by_activity_type(request: Request,
                                            vessel_id: int,
                                            activity_type: TotalTimeActivityTypeRequest = Depends(),
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            #pagination: PageParams = Depends(),
                                            #order: OrderByRequest = Depends(),
                                            caching: CachedRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    cache_key=f"{request.url.path}?{request.query_params}"
    cache_payload= rd.get(cache_key)
    start = time.time()
    payload=[]
    if cache_payload and not caching.nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=loads(cache_payload)
    else:
        use_cases = UseCases()
        db = use_cases.db()
        with db.session() as session:
            stmt=select(sql_model.Excursion.vessel_id,
                        literal_column(f"'{activity_type.type.value}'").label('activity'),
                        func.sum(sql_model.Excursion.total_time_at_sea).label("total_activity_time")
                        )\
                .select_from(sql_model.Excursion)\
                .where(
                and_(sql_model.Excursion.vessel_id == vessel_id,
                    or_(
                        sql_model.Excursion.departure_at.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Excursion.arrival_at.between(datetime_range.start_at,datetime_range.end_at),))
                )\
                .group_by(sql_model.Excursion.vessel_id)\
                .union(select(
                    literal_column(vessel_id),
                    literal_column(f"'{activity_type.type.value}'"),
                    literal_column('0 seconds'),
                ))
            print(type(session.execute(stmt.limit(1)).all()[0]))
            payload=session.execute(stmt.limit(1)).all()[0]
            serialized=dumps(payload)
            rd.set(cache_key, serialized)
            rd.expire(cache_key,settings.redis_cache_expiration)

    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload