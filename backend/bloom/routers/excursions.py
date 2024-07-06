import json
import time
from typing import List

import redis
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.domain.excursion import Excursion
from bloom.logger import logger
from bloom.usecase.Excursions import ExcursionUseCase

rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

router = APIRouter()


@router.get("/vessels/{vessel_id}/excursions")
@inject
async def list_vessel_excursions(
        vessel_id: int,
        nocache: bool = False,
        excursion_usecase: ExcursionUseCase = Depends(
            Provide[UseCasesContainer.emission_service]
        )
) -> List[Excursion]:
    endpoint = f"/vessels/{vessel_id}/excursions"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        return excursion_usecase.list_vessel_excursions(vessel_id)


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}")
async def get_vessel_excursion(
        vessel_id: int,
        excursions_id: int,
        excursion_usecase: ExcursionUseCase = Depends(
            Provide[UseCasesContainer.emission_service]
        )):
    return excursion_usecase.get_excursion_by_id(vessel_id, excursions_id)


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
@inject
async def list_vessel_excursion_segments(
        vessel_id: int,
        excursions_id: int,
        excursion_usecase: ExcursionUseCase = Depends(
            Provide[UseCasesContainer.emission_service]
        )
):
    return excursion_usecase.get_excursions_segments(vessel_id, excursions_id)


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
@inject
async def get_vessel_excursion_segment(
        vessel_id: int,
        excursions_id: int,
        segment_id: int,
        excursion_usecase: ExcursionUseCase = Depends(
            Provide[UseCasesContainer.emission_service]
        )
):
    return await excursion_usecase.get_segment_by_id(vessel_id, excursions_id, segment_id)