from fastapi import FastAPI
from fastapi import Request

from bloom.routers.v1.cache import router as router_cache_v1
from bloom.routers.v1.metrics import router as router_metrics_v1
from bloom.routers.v1.vessels import router as router_vessels_v1
from bloom.routers.v1.ports import router as router_ports_v1
from bloom.routers.v1.zones import router as router_zones_v1

from bloom.routers.v2.vessels import router as router_vessels_v2
from bloom.routers.v2.zones import router as router_zones_v2
from bloom.routers.v2.ports import router as router_ports_v2
from bloom.routers.v2.metrics import router as router_metrics_v2

from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from bloom.config import settings

API_PREFIX_V1='/api/v1'
API_PREFIX_V2='/api/v2'

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


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

@app.get("/api/v2", include_in_schema=False)
async def root_api_v2(request:Request):
    return {
            "vessels":  f"{request.url_for('list_vessels')}",
            "zones":    f"{request.url_for('list_zones')}",
            "ports":    f"{request.url_for('list_ports')}",
            "metrics":  f"{request.url_for('read_metrics_vessels_in_activity_total')}",
            }

app.include_router(router_vessels_v2,prefix=API_PREFIX_V2,tags=["Vessels_V2"])
app.include_router(router_zones_v2,prefix=API_PREFIX_V2,tags=["Zones_V2"])
app.include_router(router_ports_v2,prefix=API_PREFIX_V2,tags=["Ports_V2"])
app.include_router(router_metrics_v2, prefix=API_PREFIX_V2,tags=["Metrics_V2"])
origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://app-545ad2f8-ac5c-4926-80e2-3f487066df0e.cleverapps.io"
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
