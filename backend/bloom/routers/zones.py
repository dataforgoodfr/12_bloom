import json
import time

import redis
from fastapi import APIRouter
from starlette.requests import Request

from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.logger import logger

rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

router = APIRouter()


@router.get("/zones")
async def list_zones(request: Request, nocache: bool = False):
    endpoint = f"/zones"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in zone_repository.get_all_zones(session)]
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@router.get("/zones/all/categories")
async def list_zone_categories(request: Request, nocache: bool = False):
    endpoint = f"/zones/all/categories"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in zone_repository.get_all_zone_categories(session)]
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@router.get("/zones/by-category/{category}/by-sub-category/{sub}")
async def get_zone_all_by_category(category: str = "all", sub: str = None, nocache: bool = False):
    endpoint = f"/zones/by-category/{category}/by-sub-category/{sub}"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in
                         zone_repository.get_all_zones_by_category(session, category if category != 'all' else None,
                                                                   sub)]
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@router.get("/zones/by-category/{category}")
async def get_zone_all_by_category(category: str = "all", nocache: bool = False):
    endpoint = f"/zones/by-category/{category}"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCasesContainer()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in
                         zone_repository.get_all_zones_by_category(session, category if category != 'all' else None)]
            await rd.set(endpoint, json.dumps(json_data))
            await rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@router.get("/zones/{zones_id}")
async def get_zone(zones_id: int):
    use_cases = UseCasesContainer()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return zone_repository.get_zone_by_id(session, zones_id)
