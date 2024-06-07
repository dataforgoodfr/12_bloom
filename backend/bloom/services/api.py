from fastapi import FastAPI, APIRouter
from fastapi import Request

import redis
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger

rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

import time

app = FastAPI()


@app.get("/cache/all/flush")
async def cache_all_flush(request: Request):
    rd.flushall()
    return {"code": 0}


@app.get("/vessels")
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
        use_cases = UseCases()
        vessel_repository = use_cases.vessel_repository()
        db = use_cases.db()
        with db.session() as session:

            json_data = [json.loads(v.model_dump_json() if v else "{}")
                         for v in vessel_repository.get_vessels_list(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            return json_data


@app.get("/vessels/{vessel_id}")
async def get_vessel(vessel_id: int):
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_by_id(session, vessel_id)


@app.get("/vessels/all/positions/last")
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
        use_cases = UseCases()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in segment_repository.get_all_vessels_last_position(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@app.get("/vessels/{vessel_id}/positions/last")
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
        use_cases = UseCases()
        segment_repository = use_cases.segment_repository()
        db = use_cases.db()
        with db.session() as session:
            result = segment_repository.get_vessel_last_position(session, vessel_id)
            json_data = json.loads(result.model_dump_json() if result else "{}")
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@app.get("/vessels/{vessel_id}/excursions")
async def list_vessel_excursions(vessel_id: int, nocache: bool = False):
    endpoint = f"/vessels/{vessel_id}/excursions"
    cache = rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload = json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return payload
    else:
        use_cases = UseCases()
        excursion_repository = use_cases.excursion_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(p.model_dump_json() if p else "{}")
                         for p in excursion_repository.get_excursions_by_vessel_id(session, vessel_id)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
        return json_data


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}")
async def get_vessel_excursion(vessel_id: int, excursions_id: int):
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    with db.session() as session:
        return excursion_repository.get_vessel_excursion_by_id(session, vessel_id, excursions_id)


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
async def list_vessel_excursion_segments(vessel_id: int, excursions_id: int):
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.list_vessel_excursion_segments(session, vessel_id, excursions_id)


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
async def get_vessel_excursion_segment(vessel_id: int, excursions_id: int, segment_id: int):
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.get_vessel_excursion_segment_by_id(session, vessel_id, excursions_id, segment_id)


@app.get("/ports")
async def list_ports(request:Request,nocache:bool=False):
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



@app.get("/ports/{port_id}")
async def get_port(port_id: int):
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        return port_repository.get_port_by_id(session, port_id)


@app.get("/zones")
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
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in zone_repository.get_all_zones(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@app.get("/zones/all/categories")
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
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in zone_repository.get_all_zone_categories(session)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@app.get("/zones/by-category/{category}/by-sub-category/{sub}")
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
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in
                         zone_repository.get_all_zones_by_category(session, category if category != 'all' else None,
                                                                   sub)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data


@app.get("/zones/by-category/{category}")
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
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in
                         zone_repository.get_all_zones_by_category(session, category if category != 'all' else None)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint, settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time() - start}")
            return json_data

@app.get("/zones/by-category/{category}/by-sub-category/{sub}")
async def get_zone_all_by_category(category:str,sub:str=None,nocache:bool=False):
    endpoint=f"/zones/by-category/{category}/by-sub-category/{sub}"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [json.loads(z.model_dump_json() if z else "{}")
                         for z in zone_repository.get_all_zones_by_category(session,category if category != 'all' else None,sub)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
            return json_data

@app.get("/zones/by-category/{category}")
async def get_zone_all_by_category(category:str="amp",nocache:bool=0):
    endpoint=f"/zones/by-category/{category}"
    cache= rd.get(endpoint)
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{endpoint} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [z.model_dump_json()
                         for z in zone_repository.get_all_zones_by_category(session,category)]
            rd.set(endpoint, json.dumps(json_data))
            rd.expire(endpoint,settings.redis_cache_expiration)
            logger.debug(f"{endpoint} elapsed Time: {time.time()-start}")
            return json_data

@app.get("/zones/{zones_id}")
async def get_zone(zones_id: int):
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return zone_repository.get_zone_by_id(session, zones_id)


@app.get("/")
async def root(request: Request):
    return {
        "cache_all_flush": f"{request.url_for('cache_all_flush')}",
        "ports": f"{request.url_for('list_ports')}",
        "vessels": f"{request.url_for('list_vessels')}",
        "zones": f"{request.url_for('list_zones')}",
    }
