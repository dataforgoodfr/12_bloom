from fastapi import APIRouter, Depends, Request
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from bloom.dependencies import ( X_API_KEY_HEADER,check_apikey)
from bloom.config import settings
from bloom.domain.port import PostListView
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/ports")
async def list_ports(   request:Request,
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
async def get_port(port_id:int,
                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    port_repository = use_cases.port_repository()
    db = use_cases.db()
    with db.session() as session:
        return port_repository.get_port_by_id(session,port_id)