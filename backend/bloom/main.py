from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.security import APIKeyHeader

from bloom.routers.metrics import router as router_metrics
from bloom.routers.vessels import router as router_vessels
from bloom.routers.ports import router as router_ports
from bloom.routers.zones import router as router_zones
from bloom.dependencies import (  DatetimeRangeRequest,
                                 PaginatedRequest,OrderByRequest,
                                 paginate,PagedResponseSchema,PageParams,
                                 X_API_KEY_HEADER,check_apikey)

import redis
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.logger import logger

rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

from datetime import datetime
import time


app = FastAPI()
app.include_router(router_metrics)
app.include_router(router_vessels)
app.include_router(router_ports)
app.include_router(router_zones)



@app.get("/cache/all/flush")
async def cache_all_flush(request:Request,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    rd.flushall()
    return {"code":0}

@app.get("/")
async def root(request:Request):
    return {
            "cache_all_flush": f"{request.url_for('cache_all_flush')}",
            "ports":    f"{request.url_for('list_ports')}",
            "vessels":  f"{request.url_for('list_vessels')}",
            "zones":    f"{request.url_for('list_zones')}",
            }