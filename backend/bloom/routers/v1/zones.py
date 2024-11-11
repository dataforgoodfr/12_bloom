from fastapi import APIRouter, Depends, HTTPException, Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
import time
import redis
import json
from sqlalchemy import select, func, and_, or_
from bloom.infra.database import sql_model
from bloom.infra.repositories.repository_segment import SegmentRepository
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.logger import logger
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey,cache)

router = APIRouter()

@router.get("/zones")
@cache
async def list_zones(request:Request,nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)  
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json() if z else "{}")
                        for z in zone_repository.get_all_zones(session)]
        return json_data

@router.get("/zones/all/categories")
@cache
async def list_zone_categories(request:Request,nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json()  if z else "{}")
                        for z in zone_repository.get_all_zone_categories(session)]
        return json_data

@router.get("/zones/by-category/{category}/by-sub-category/{sub}")
@cache
async def get_zone_all_by_category(category:str="all",sub:str=None,nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json() if z else "{}")
                        for z in zone_repository.get_all_zones_by_category(session,category if category != 'all' else None,sub)]
        return json_data

@router.get("/zones/by-category/{category}")
@cache
async def get_zone_all_by_category(category:str="all",nocache:bool=False,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        json_data = [json.loads(z.model_dump_json() if z else "{}")
                        for z in zone_repository.get_all_zones_by_category(session,category if category != 'all' else None)]
        return json_data
        
@router.get("/zones/{zones_id}")
@cache
async def get_zone(zones_id:int,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    zone_repository = use_cases.zone_repository()
    db = use_cases.db()
    with db.session() as session:
        return zone_repository.get_zone_by_id(session,zones_id)