from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated
import json
from bloom.container import UseCases
from bloom.domain.zone import ZoneListView
from bloom.dependencies import (X_API_KEY_HEADER,
                                check_apikey)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bloom.dependencies import (
    RangeHeader,
    RangeHeaderParser,
    PaginatedJSONResponse,
    UsingCacheQuery,
    CacheKey
)


router = APIRouter()


@router.get("/zones")
async def list_zones(request: Request,
                     key: str = Depends(X_API_KEY_HEADER),
                     range: Annotated[RangeHeader, Depends(RangeHeaderParser)] = None,
                     use_cache: Annotated[bool, Depends(UsingCacheQuery)]= None,
                     cache_key: Annotated[str,Depends(CacheKey)]=None):
    check_apikey(key)
    print(f"Range:{range}")
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    cache=UseCases.cache_service()
    payload=cache.get(cache_key)
    if not use_cache or payload is None:
        with db.session() as session:
            # Récupération d'un PaginatedSqlResult[list[Zone]]
            # range correspond aux plages demandée dans la requête
            result = zone_repository.get_all_zones(session, range=range)
            # Génération de la réponse HTTP 200/206 + headers selon présence ou non
            # d'un paramètre range dans la requête
            response= PaginatedJSONResponse(result=result,
                                        request=request)
            #cache.set(cache_key,json.dumps(jsonable_encoder(result)))
    else:
        response=[] #response= PaginatedJSONResponse(**json.loads(cache.get(cache_key)))
    return response
        


@router.get("/zones/summary") 
async def list_zones_summary(request: Request,
                             key: str = Depends(X_API_KEY_HEADER),
                             ):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        result = zone_repository.get_all_zones_summary(session)
    return result


@router.get("/zones/categories")
async def list_zone_categories(request: Request, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [z for z in zone_repository.get_all_zone_categories(session)]
        return json_data


@router.get("/zones/by-category/{category}/by-sub-category/{sub}")
async def get_zone_all_by_category(request: Request, category: str = "all", sub: str = None,
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
async def get_zone_all_by_category(request: Request, category: str = "all",
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
async def get_zone(request: Request, zones_id: int, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return jsonable_encoder(zone_repository.get_zone_by_id(session, zones_id))
