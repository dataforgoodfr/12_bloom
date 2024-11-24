from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated
import json
from bloom.container import UseCases
from bloom.domain.zone import ZoneListView
from bloom.dependencies import (X_API_KEY_HEADER,
                                check_apikey,
                                cache)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bloom.routers.requests import (
    RangeHeader,
    RangeHeaderParser
)


router = APIRouter()


@router.get("/zones")
# @cache
async def list_zones(request: Request,
                     nocache: bool = False,
                     key: str = Depends(X_API_KEY_HEADER),
                     range: Annotated[RangeHeader, Depends(RangeHeaderParser)] = None):
    check_apikey(key)
    print(f"Range:{range}")
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        result = zone_repository.get_all_zones(session, range=range)
        """payload = [ZoneListView(**z.model_dump())
                        for z,total in zone_repository.get_all_zones(session,range=range)]"""

        response = JSONResponse(content=jsonable_encoder(result.payload),
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


@router.get("/zones/categories")
@cache
async def list_zone_categories(request: Request, nocache: bool = False, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [z for z in zone_repository.get_all_zone_categories(session)]
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
