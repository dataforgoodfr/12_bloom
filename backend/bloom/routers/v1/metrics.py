from fastapi import APIRouter, Depends, Query, Body,Request
import redis
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
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

@router.get("/metrics/vessels-in-activity",
            response_model=list[ResponseMetricsVesselInActivitySchema])
def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    cache_key=f"{request.url.path}?{request.query_params}"
    cache_payload= rd.get(cache_key)
    start = time.time()
    payload = []
    if cache_payload and not caching.nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=loads(cache_payload)
    else:
        use_cases = UseCases()
        MetricsService=use_cases.metrics_service()
        payload=MetricsService.getVesselsInActivity(datetime_range=datetime_range,
                                                    pagination=pagination,
                                                    order=order)
        serialized=dumps(payload)
        rd.set(cache_key, serialized)
        rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload

@router.get("/metrics/zone-visited",
            response_model=list[ResponseMetricsZoneVisitedSchema])
def read_zone_visited_total(request: Request,
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
        MetricsService=use_cases.metrics_service()
        payload=MetricsService.getZoneVisited(datetime_range=datetime_range,
                                                    pagination=pagination,
                                                    order=order)
        serialized=dumps(payload)
        rd.set(cache_key, serialized)
        rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload

@router.get("/metrics/zones/{zone_id}/visiting-time-by-vessel",
            response_model=list[ResponseMetricsZoneVisitingTimeByVesselSchema])
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
        MetricsService=use_cases.metrics_service()
        payload=MetricsService.getZoneVisitingTimeByVessel(
                                                    zone_id=zone_id,
                                                    datetime_range=datetime_range,
                                                    pagination=pagination,
                                                    order=order)
        serialized=dumps(payload)
        rd.set(cache_key, serialized)
        rd.expire(cache_key,settings.redis_cache_expiration)
    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload


@router.get("/metrics/vessels/{vessel_id}/activity/{activity_type}",
            response_model=ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema)
def read_metrics_vessels_visits_by_activity_type(request: Request,
                                            vessel_id: int,
                                            activity_type: TotalTimeActivityTypeRequest = Depends(),
                                            datetime_range: DatetimeRangeRequest = Depends(),
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
        MetricsService=use_cases.metrics_service()
        payload=MetricsService.getVesselVisitsByActivityType(
                                                    vessel_id=vessel_id,
                                                    activity_type=activity_type,
                                                    datetime_range=datetime_range)
        serialized=dumps(payload)
        rd.set(cache_key, serialized)
        rd.expire(cache_key,settings.redis_cache_expiration)

    logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
    return payload