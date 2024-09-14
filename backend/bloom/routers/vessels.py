from fastapi import APIRouter

from redis import Redis
import json
import time
from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.logger import logger

rd = Redis(host=settings.redis_host, port=settings.redis_port, db=0)


router = APIRouter()


@router.get("/vessels")
async def list_vessels(nocache: bool = False):
    endpoint = f"/vessels"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        vessel_repository = use_cases.vessel_repository()
        db = use_cases.db()
        with db.session() as session:

            json_data = [json.loads(v.model_dump_json() if v else "{}")
                         for v in vessel_repository.get_vessels_list(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            return json_data


@router.get("/vessels/{vessel_id}")
async def get_vessel(vessel_id: int):
    use_cases = UseCasesContainer()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_by_id(session, vessel_id)


@router.get("/vessels/all/positions/last")
async def list_all_vessel_last_position(nocache: bool = False):
    endpoint = f"/vessels/all/positions/last"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in segment_repository.get_all_vessels_last_position(session)]
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@router.get("/vessels/{vessel_id}/positions/last")
async def get_vessel_last_position(vessel_id: int, nocache: bool = False):
    endpoint = f"/vessels/{vessel_id}/positions/last"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            result = segment_repository.get_vessel_last_position(session, vessel_id)
            json_data = json.loads(result.model_dump_json() if result else "{}")
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data
