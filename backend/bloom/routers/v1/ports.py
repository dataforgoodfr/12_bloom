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
        json_data = [json.loads(p.model_dump_json() if p else "{}")
                        for p in port_repository.get_all_ports(session)]
        return json_data
    

@router.get("/ports/{port_id}")
@cache
async def get_port(port_id:int,
                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        return port_repository.get_port_by_id(session,port_id)