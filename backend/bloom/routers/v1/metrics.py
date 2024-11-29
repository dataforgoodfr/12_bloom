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
from bloom.domain.vessel import Vessel
from bloom.infra.database.database_manager import Base
from bloom.domain.metrics import (ResponseMetricsVesselInActivitySchema,
                                 ResponseMetricsZoneVisitedSchema,
                                 ResponseMetricsZoneVisitingTimeByVesselSchema,
                                 ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema)
from bloom.routers.requests import DatetimeRangeRequest,OrderByRequest,PageParams,CachedRequest
from bloom.dependencies import ( X_API_KEY_HEADER, check_apikey,cache)
from bloom.routers.requests import (
    RangeHeader,
    RangeHeaderParser
)

from bloom.domain.metrics import TotalTimeActivityTypeRequest
from fastapi.encoders import jsonable_encoder

router = APIRouter()
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

@router.get("/metrics/vessels-in-activity")
@cache
async def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    MetricsService=use_cases.metrics_service()
    payload=MetricsService.getVesselsInActivity(datetime_range=datetime_range,
                                                pagination=pagination,
                                                order=order)
    
    return jsonable_encoder(payload)


@router.get("/metrics/zone-visited")
@cache
async def read_zone_visited_total(
    request: Request,
    datetime_range: DatetimeRangeRequest = Depends(),
    category: Optional[str] = None,
    pagination: PageParams = Depends(),
    order: OrderByRequest = Depends(),
    caching: CachedRequest = Depends(),
    key: str = Depends(X_API_KEY_HEADER),
):
    check_apikey(key)
    use_cases = UseCases()
    MetricsService=use_cases.metrics_service()
    payload=MetricsService.getZoneVisited(datetime_range=datetime_range,
                                          category=category,
                                                pagination=pagination,
                                                order=order)
    return jsonable_encoder(payload)


@router.get("/metrics/zones/{zone_id}/visiting-time-by-vessel")
@cache
async def read_metrics_zone_visiting_time_by_vessel(request: Request,
                                            zone_id: int,
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            pagination: PageParams = Depends(),
                                            order: OrderByRequest = Depends(),
                                            caching: CachedRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    use_cases = UseCases()
    MetricsService=use_cases.metrics_service()
    payload=MetricsService.getZoneVisitingTimeByVessel(
                                                zone_id=zone_id,
                                                datetime_range=datetime_range,
                                                pagination=pagination,
                                                order=order)
    return jsonable_encoder(payload)

@router.get("/metrics/vessels/time-by-zone")
# @cache
async def read_metrics_all_vessels_visiting_time_by_zone(request: Request,
                                            vessel_id: Optional[int] = None,
                                            category: Optional[str] = None,
                                            sub_category: Optional[str] = None,
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            pagination: PageParams = Depends(),
                                            order: OrderByRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    use_cases = UseCases()
    MetricsService=use_cases.metrics_service()
    payload=MetricsService.getVesselVisitingTimeByZone(
                                                vessel_id=vessel_id,
                                                datetime_range=datetime_range,
                                                pagination=pagination,
                                                order=order,
                                                category=category,
                                                sub_category=sub_category)
    return jsonable_encoder(payload)
