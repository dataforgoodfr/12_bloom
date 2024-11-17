from fastapi import APIRouter, Depends, HTTPException, Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
import time
import redis
import json
from sqlalchemy import select, func, and_, or_
from bloom.infra.database import sql_model
from bloom.infra.repositories.repository_segment import SegmentRepository
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.logger import logger
from bloom.dependencies import (  DatetimeRangeRequest,
                                PaginatedRequest,OrderByRequest,OrderByEnum,
                                paginate,PagedResponseSchema,PageParams,
                                X_API_KEY_HEADER,check_apikey)

router = APIRouter()
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

@router.get("/vessels")
async def list_vessels(nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    endpoint=f"/vessels"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        db = use_cases.db()
        with db.session() as session:
            vessel_repository = use_cases.vessel_repository(session)
            json_data = [json.loads(v.model_dump_json() if v else "{}")
                            for v in vessel_repository.list()]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            return json_data

@router.get("/vessels/{vessel_id}")
async def get_vessel(request: Request, vessel_id: int,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        vessel_repository = use_cases.vessel_repository(session)
        return vessel_repository.get_by_id(id=vessel_id)

@router.get("/vessels/all/positions/last")
async def list_all_vessel_last_position(nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    endpoint=f"/vessels/all/positions/last"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in segment_repository.get_all_vessels_last_position(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
            return json_data

@router.get("/vessels/{vessel_id}/positions/last")
async def get_vessel_last_position(vessel_id: int, nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    endpoint=f"/vessels/{vessel_id}/positions/last"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            result=segment_repository.get_vessel_last_position(session,vessel_id)
            json_data = json.loads(result.model_dump_json() if result else "{}")
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
            return json_data

@router.get("/vessels/{vessel_id}/excursions")
async def list_vessel_excursions(vessel_id: int, nocache:bool=False,
                                datetime_range: DatetimeRangeRequest = Depends(),
                                pagination: PageParams = Depends(),
                                order: OrderByRequest = Depends(),
                                key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    endpoint=f"/vessels/{vessel_id}/excursions"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        excursion_repository = use_cases.excursion_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in excursion_repository.get_excursions_by_vessel_id(session,vessel_id)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return json_data


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}")
async def get_vessel_excursion(vessel_id: int,excursions_id: int,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    with db.session() as session:
        return excursion_repository.get_vessel_excursion_by_id(session,vessel_id,excursions_id)


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
async def list_vessel_excursion_segments(vessel_id: int,
                                         excursions_id: int,
                                         key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.list_vessel_excursion_segments(session,vessel_id,excursions_id)

@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
async def get_vessel_excursion_segment(vessel_id: int,
                                       excursions_id: int,
                                       segment_id:int,
                                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.get_vessel_excursion_segment_by_id(session,vessel_id,excursions_id,segment_id)