from fastapi import FastAPI
from fastapi import Request

from bloom.routers.v1.cache import router as router_cache_v1
from bloom.routers.v1.metrics import router as router_metrics_v1
from bloom.routers.v1.vessels import router as router_vessels_v1
from bloom.routers.v1.ports import router as router_ports_v1
from bloom.routers.v1.zones import router as router_zones_v1
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from bloom.config import settings

API_PREFIX_V1='/api/v1'

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
