from fastapi import FastAPI, APIRouter
from fastapi import Request

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

@app.get("/cache/all/flush")
async def cache_all_flush(request:Request):
    rd.flushall()
    return {"code":0}

@app.get("/vessels")
async def list_vessels():
    cache= rd.get(app.url_path_for('list_vessels'))
    if cache:
        return json.loads(cache)
    else:
        use_cases = UseCases()
        vessel_repository = use_cases.vessel_repository()
        db = use_cases.db()
        with db.session() as session:
            
            json_data = [v.model_dump_json()
                            for v in vessel_repository.get_vessels_list(session)]
            rd.set(app.url_path_for('list_vessels'), json.dumps(json_data))
            rd.expire(app.url_path_for('list_vessels'),settings.redis_cache_expiration)
            return json_data

@app.get("/vessels/{vessel_id}")
async def get_vessel(vessel_id: int):
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_by_id(session,vessel_id)

@app.get("/vessels/all/positions/last")
async def list_all_vessel_last_position():
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.get_all_vessels_last_position(session)

@app.get("/vessels/{vessel_id}/positions/last")
async def get_vessel_last_position(vessel_id: int):
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.get_vessel_last_position(session,vessel_id)

@app.get("/vessels/{vessel_id}/excursions")
async def list_vessel_excursions(vessel_id: int):
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    with db.session() as session:
        return excursion_repository.get_excursions_by_vessel_id(session,vessel_id)


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}")
async def get_vessel_excursion(vessel_id: int,excursions_id: int):
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    with db.session() as session:
        return excursion_repository.get_vessel_excursion_by_id(session,vessel_id,excursions_id)


@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
async def list_vessel_excursion_segments(vessel_id: int,excursions_id: int):
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.list_vessel_excursion_segments(session,vessel_id,excursions_id)

@app.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
async def get_vessel_excursion_segment(vessel_id: int,excursions_id: int, segment_id:int):
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.get_vessel_excursion_segment_by_id(session,vessel_id,excursions_id,segment_id)

@app.get("/ports")
async def list_ports(request:Request,nocache:bool=0):
    cache= rd.get(app.url_path_for('list_ports'))
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{app.url_path_for('list_ports')} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{app.url_path_for('list_ports')} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        port_repository = use_cases.port_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [p.model_dump_json()
                         for p in port_repository.get_all_ports(session)]
            rd.set(app.url_path_for('list_ports'), json.dumps(json_data))
            rd.expire(app.url_path_for('list_ports'),settings.redis_cache_expiration)
            logger.debug(f"{app.url_path_for('list_ports')} elapsed Time: {time.time()-start}")
            return json_data
    

@app.get("/ports/{port_id}")
async def get_port(port_id:int):
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        return port_repository.get_port_by_id(session,port_id)

@app.get("/vessels/all/positions/last")
async def list_vessel_positions(vessel_id: int, date:datetime=datetime.now()):
    use_cases = UseCases()
    vessel_position_repository = use_cases.vessel_position_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_position_repository.get_vessel_positions(session,vessel_id)
        
@app.get("/zones")
async def list_zones(request:Request,nocache:bool=0):   
    cache= rd.get(app.url_path_for('list_zones'))
    start = time.time()
    if cache and not nocache:
        logger.debug(f"{app.url_path_for('list_zones')} cached ({settings.redis_cache_expiration})s")
        payload=json.loads(cache)
        logger.debug(f"{app.url_path_for('list_zones')} elapsed Time: {time.time()-start}")
        return payload
    else:
        use_cases = UseCases()
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            json_data = [z.model_dump_json()
                         for z in zone_repository.get_all_zones(session)]
            rd.set(app.url_path_for('list_zones'), json.dumps(json_data))
            rd.expire(app.url_path_for('list_zones'),settings.redis_cache_expiration)
            logger.debug(f"{app.url_path_for('list_zones')} elapsed Time: {time.time()-start}")
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
async def get_zone(zones_id:int):
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return zone_repository.get_zone_by_id(session,zones_id)



@app.get("/statics/{zones}")
async def get_statics_zones():
    return {}

@app.get("/maptiles/mpa")
async def get_maptile_mpa():
    return {"data":{}}

@app.get("/maptiles/territorial")
async def get_maptile_territorial():
    return {"data":{}}

@app.get("/maptiles/coastal")
async def get_maptile_coastal():
    return {"data":{}}

@app.get("/maptiles")
async def list_maptiles(request:Request):
    return {
                "mpa":          f"{request.url_for('get_maptile_mpa')}",
                "territorial":  f"{request.url_for('get_maptile_territorial')}",
                "coastal":      f"{request.url_for('get_maptile_coastal')}",
            }

@app.get("/maptiles")
async def list_maptiles():
    return {"data":{}}

@app.get("/")
async def root(request:Request):
    return {
            "maptiles": f"{request.url_for('list_maptiles')}",
            "ports":    f"{request.url_for('list_ports')}",
            "vessels":  f"{request.url_for('list_vessels')}",
            "zones":    f"{request.url_for('list_zones')}",
            }