from fastapi import APIRouter, Depends, Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from bloom.routers.requests import CachedRequest
from bloom.dependencies import ( X_API_KEY_HEADER,check_apikey,cache)
from bloom.config import settings
from bloom.domain.port import PostListView
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/ports")
@cache
async def list_ports(   request:Request,
                        caching: CachedRequest = Depends(),
                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        payload = [PostListView(**p.model_dump())
                        for p in port_repository.get_all_ports(session)]
        return jsonable_encoder(payload)
    

@router.get("/ports/{port_id}")
@cache
async def get_port(port_id:int,
                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        port_repository = use_cases.port_repository(session)
        return port_repository.get_by_id(port_id)