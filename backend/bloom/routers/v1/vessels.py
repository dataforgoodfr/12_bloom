from fastapi import APIRouter, Depends, Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from typing import Any, Optional
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from bloom.routers.requests import DatetimeRangeRequest,OrderByRequest,PageParams
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey,cache)
from fastapi.encoders import jsonable_encoder
from datetime import datetime

router = APIRouter()


@router.get("/vessels/trackedCount")
async def list_vessel_tracked(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_tracked_count(session)

@router.get("/vessels/types")
async def list_vessel_types(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_types(session)


@router.get("/vessels/classes")
async def list_vessel_classes(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_length_classes(session)

@router.get("/vessels/countries")
async def list_vessel_countries(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return vessel_repository.get_vessel_countries(session)


@router.get("/vessels")
@cache
async def list_vessels(request: Request, # used by @cache
                       nocache:bool=False, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        return jsonable_encoder(vessel_repository.get_vessels_list(session))

@router.get("/vessels/{vessel_id}")
@cache
async def get_vessel(request: Request, # used by @cache
                     vessel_id: int,
                     nocache:bool=False, # used by @cache
                     key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        data=vessel_repository.get_vessel_by_id(session,vessel_id)
        return json.loads(vessel_repository.map_to_domain(data).model_dump_json()) if data else {}

@router.get("/vessels/all/positions/last")
@cache
async def list_all_vessel_last_position(request: Request, # used by @cache
                                        nocache:bool=False, # used by @cache
                                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        json_data = [json.loads(p.model_dump_json() if p else "{}")
                        for p in segment_repository.get_all_vessels_last_position(session)]
    return json_data


@router.get("/vessels/all/positions/at")
@cache
async def list_all_vessel_position_at(
    request: Request,  # used by @cache
    timestamp: datetime,
    nocache: bool = False,  # used by @cache
    key: str = Depends(X_API_KEY_HEADER),
):
    check_apikey(key)
    use_cases = UseCases()
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    json_data = {}
    with db.session() as session:
        json_data = [
            json.loads(p.model_dump_json() if p else "{}")
            for p in segment_repository.get_all_vessels_positions_at(session, timestamp)
        ]
    return json_data


@router.get("/vessels/{vessel_id}/positions/last")
@cache
async def get_vessel_last_position(request: Request, # used by @cache
                                   vessel_id: int,
                                   nocache:bool=False, # used by @cache
                                   key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        result=segment_repository.get_vessel_last_position(session,vessel_id)
        json_data = json.loads(result.model_dump_json() if result else "{}")
    return json_data

@router.get("/vessels/{vessel_id}/excursions")
@cache
async def list_vessel_excursions(request: Request, # used by @cache
                                 vessel_id: int,
                                 nocache:bool=False, # used by @cache
                                datetime_range: DatetimeRangeRequest= Depends(),
                                pagination: PageParams = Depends(),
                                order: OrderByRequest = Depends(),
                                key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        json_data = [json.loads(p.model_dump_json() if p else "{}")
                        for p in excursion_repository.get_excursions_by_vessel_id(
                                                    session,
                                                    vessel_id,
                                                    datetime_range,
                                                    pagination=pagination,
                                                    order=order)]
    return json_data


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}")
@cache
async def get_vessel_excursion(request: Request, # used by @cache
                               vessel_id: int,
                               excursions_id: int,
                               nocache:bool=False, # used by @cache
                               key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        result = excursion_repository.get_vessel_excursion_by_id(session,vessel_id,excursions_id)
        json_data = json.loads(result.model_dump_json() if result else "{}")
    return json_data


@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments")
@cache
async def list_vessel_excursion_segments(request: Request, # used by @cache
                                         vessel_id: int,
                                         excursions_id: int,
                                         nocache:bool=False, # used by @cache
                                         key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    with db.session() as session:
        return segment_repository.list_vessel_excursion_segments(session,vessel_id,excursions_id)

@router.get("/vessels/{vessel_id}/excursions/{excursions_id}/segments/{segment_id}")
@cache
async def get_vessel_excursion_segment(request: Request, # used by @cache
                                       vessel_id: int,
                                       excursions_id: int,
                                       segment_id:int,
                                       nocache:bool=False, # used by @cache
                                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    segment_repository = use_cases.segment_repository()
    db = use_cases.db()
    json_data={}
    with db.session() as session:
        result = segment_repository.get_vessel_excursion_segment_by_id(session,vessel_id,excursions_id,segment_id)
        json_data = json.loads(result.model_dump_json() if result else "{}")
    return json_data
