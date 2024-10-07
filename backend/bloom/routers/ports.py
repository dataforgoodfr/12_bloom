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
from bloom.domain.metrics import (ResponseMetricsVesselInActiviySchema,
                                 ResponseMetricsZoneVisitedSchema,
                                 ResponseMetricsZoneVisitingTimeByVesselSchema)
from bloom.domain.api import (  DatetimeRangeRequest,
                                PaginatedRequest,OrderByRequest,OrderByEnum,
                                paginate,PagedResponseSchema,PageParams,
                                X_API_KEY_HEADER,check_apikey)
from bloom.config import settings

router = APIRouter()
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

@router.get("/ports",
         tags=['Ports'])
async def list_ports(request:Request,nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    endpoint=f"/ports"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        port_repository = use_cases.port_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in port_repository.get_all_ports(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
            return json_data
    

@router.get("/ports/{port_id}",
         tags=['Ports'])
async def get_port(port_id:int,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        return port_repository.get_port_by_id(session,port_id)