from fastapi import APIRouter, Depends, Request
from bloom.config import settings
import redis
from bloom.config import settings
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey)
from bloom.container import UseCases

router = APIRouter()

@router.get("/cache/all/flush")
async def cache_all_flush(request:Request,key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    UseCases().cache_service().flushall()
    return {"code":0}