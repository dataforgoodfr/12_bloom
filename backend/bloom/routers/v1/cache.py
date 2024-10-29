from fastapi import APIRouter, Depends, Request
from bloom.config import settings
import redis
from bloom.config import settings
from bloom.logger import logger
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey)

router = APIRouter()
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

@router.get("/cache/all/flush")
async def cache_all_flush(request:Request,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    rd.flushall()
    return {"code":0}