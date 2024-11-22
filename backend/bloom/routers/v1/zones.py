from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated, Any
import json
from bloom.container import UseCases
from bloom.domain.zone import ZoneListView
from bloom.dependencies import (X_API_KEY_HEADER,
                                check_apikey,
                                cache,cache_json_response)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bloom.routers.requests import (
    RangeHeader,
    RangeHeaderParser
)
from fastapi import FastAPI
from bloom.config import settings
from bloom.routers.requests import RangeHeader, PaginatedResult, NonPaginatedResult


router = APIRouter()

def get_cached_key(request: Request):
    return f"{request.url.path}/{request.query_params}#range:{request.headers.get('range','')}"

def get_cached_payload(request: Request):
    cachekey=f"{request.url.path}/{request.query_params}#range:{request.headers.get('range','')}"
    nocache=request.query_params.get('nocache',False).lower() == 'true'
    use_cases = UseCases()
    cache=use_cases.cache_service()
    incache=cache.get(cachekey)
    print(f"### TEST {incache is not None and not nocache}. incache {incache is not None} {not nocache}")
    payload=None
    if (incache is not None and not nocache):
        payload=incache.decode()
    return payload

@router.get("/zones")
# @cache
#@cache_json_response
async def list_zones(request: Request,
                     nocache: bool = False,
                     key: str = Depends(X_API_KEY_HEADER),
                     range: Annotated[RangeHeader, Depends(RangeHeaderParser)] = None,
                     cached_key: Annotated[str,Depends(get_cached_key)]=None,
                     cached_payload: Annotated[Any, Depends(get_cached_payload)] = None):
    check_apikey(key)
    use_cases = UseCases()
    payload=None
    if cached_payload is not None:
        print("### Get from cache")
        response=PaginatedResult(**json.loads(cached_payload.decode()))
        print(response)
    else:
        zone_repository = use_cases.zone_repository()
        db = use_cases.db()
        with db.session() as session:
            result = zone_repository.get_all_zones(session, range=range)
            use_cases = UseCases()
            cache=use_cases.cache_service()
            cache.set(cached_key,json.dumps(jsonable_encoder(result)).encode())
            cache.expire(cached_key,settings.redis_cache_expiration)
    response = JSONResponse(content=payload,
                            status_code=206 if range is not None else 200)
    if result.spec is not None:
        for s in result.spec:
            response.headers.append(key='Content-Range',
                                    value=f"{s.start if s.start != None else ''}-{s.end if s.end != None else ''}/{result.total}")

    return response


@router.get("/zones/summary")
# @cache
async def list_zones_summary(request: Request,
                             nocache: bool = False,
                             key: str = Depends(X_API_KEY_HEADER),
                             ):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        result = zone_repository.get_all_zones_summary(session)
    return result


@router.get("/zones/all/categories")
@cache
async def list_zone_categories(request: Request, nocache: bool = False, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [ZoneListView(**z.model_dump_json())
                     for z in zone_repository.get_all_zone_categories(session)]
        return json_data


@router.get("/zones/by-category/{category}/by-sub-category/{sub}")
@cache
async def get_zone_all_by_category(request: Request, category: str = "all", sub: str = None, nocache: bool = False,
                                   key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json() if z else "{}")
                     for z in
                     zone_repository.get_all_zones_by_category(session, category if category != 'all' else None, sub)]
        return json_data


@router.get("/zones/by-category/{category}")
@cache
async def get_zone_all_by_category(request: Request, category: str = "all", nocache: bool = False,
                                   key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json() if z else "{}")
                     for z in
                     zone_repository.get_all_zones_by_category(session, category if category != 'all' else None)]
        return json_data


@router.get("/zones/{zones_id}")
@cache
async def get_zone(request: Request, zones_id: int, nocache: bool = False, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return jsonable_encoder(zone_repository.get_zone_by_id(session, zones_id))
