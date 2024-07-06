from fastapi import FastAPI
from starlette.requests import Request

from bloom.container import UseCasesContainer
from bloom.routers import excursions, zones, vessels, ports
from bloom.routers.vessels import router, rd


def init_db(container):
    db = container.db()
    db.create_database()


def create_app() -> FastAPI:
    container = init_container()

    init_db(container)
    server = init_server(container)
    # server.add_exception_handler(DBException, db_exception_handler)
    # server.add_exception_handler(ValidationError, validation_exception_handler)
    # server.add_exception_handler(Exception, generic_exception_handler)

    return server


def schedule_crawling():
    pass

def init_container():
    container = UseCasesContainer()
    container.wire(
        modules=[
            zones,
            vessels,
            excursions,
            ports
        ]
    )
    return container


def init_server(container):
    server = FastAPI(dependencies=[])
    server.container = container
    server.include_router(excursions.router)
    server.include_router(ports.router)
    server.include_router(vessels.router)
    server.include_router(zones.router)
    return server


app = create_app()


@app.get("/")
async def root(request: Request):
    return {
        "maptiles": f"{request.url_for('list_maptiles')}",
        "ports": f"{request.url_for('list_ports')}",
        "vessels": f"{request.url_for('list_vessels')}",
        "zones": f"{request.url_for('list_zones')}",
    }


@app.get("/cache/all/flush")
async def cache_all_flush(request: Request):
    await rd.flushall()
    return {"code": 0}
