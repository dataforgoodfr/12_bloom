from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.security import APIKeyHeader

from bloom.routers.v1.cache import router as router_cache_v1
from bloom.routers.v1.metrics import router as router_metrics_v1
from bloom.routers.v1.vessels import router as router_vessels_v1
from bloom.routers.v1.ports import router as router_ports_v1
from bloom.routers.v1.zones import router as router_zones_v1
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

API_PREFIX_V1='/api/v1'

app = FastAPI()


@app.get("/", include_in_schema=False)
@app.get("/api", include_in_schema=False)
async def root(request:Request):
    return {
            "v1": f"{request.url_for('root_api_v1')}",
            }

@app.get("/api/v1", include_in_schema=False)
async def root_api_v1(request:Request):
    return {
            "cache":    f"{request.url_for('cache_all_flush')}",
            "ports":    f"{request.url_for('list_ports')}",
            "vessels":  f"{request.url_for('list_vessels')}",
            "zones":    f"{request.url_for('list_zones')}",
            }

app.include_router(router_cache_v1,prefix=API_PREFIX_V1,tags=["Cache"])
app.include_router(router_metrics_v1,prefix=API_PREFIX_V1,tags=["Metrics"])
app.include_router(router_ports_v1,prefix=API_PREFIX_V1,tags=["Ports"])
app.include_router(router_vessels_v1,prefix=API_PREFIX_V1,tags=["Vessels"])
app.include_router(router_zones_v1,prefix=API_PREFIX_V1,tags=["Zones"])


