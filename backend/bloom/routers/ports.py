import json
import time

from redis import Redis
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.logger import logger
from bloom.usecase.Ports import PortUseCase

router = APIRouter()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)


@router.get("/ports")
@inject
async def list_ports(
        nocache: bool = False,
        ports_usecase: PortUseCase = Depends(
            Provide[UseCasesContainer.excursion_usecase]
        )
):
    endpoint = f"/ports"
    cache = redis_client.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        return ports_usecase.list_ports()


@router.get("/ports/{port_id}")
@inject
async def get_port(
        port_id: int,
        ports_usecase: PortUseCase = Depends(
            Provide[UseCasesContainer.excursion_usecase]
        )
):
    return ports_usecase.get_port_by_id(port_id)
