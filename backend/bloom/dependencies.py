from fastapi import Request, HTTPException, Depends
from bloom.config import settings
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from functools import wraps
import time
import json
from bloom.logger import logger
from bloom.container import UseCases

## Reference for pagination design
## https://jayhawk24.hashnode.dev/how-to-implement-pagination-in-fastapi-feat-sqlalchemy
X_API_KEY_HEADER=APIKeyHeader(name="x-key")


## FastAPI endpoint decorator to manage Redis caching
# Needs to add request:Request and nocache:bool parameters to all endpoints
# using @cache decorator
# Example:
# @router.get('/my/endpoint')
# @cache
# def my_endpoint_function(request: Request,         # needed by @cache
#                          ...
#                          nocache:bool = False,    # needed by @cache
#                        ):
#         ...
def cache(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        request=kwargs['request']
        cache_service=UseCases().cache_service()
        nocache=True if request.query_params.get('nocache') \
                            and request.query_params.get('nocache').lower() == 'true' \
                     else False
        cache_key=f"{request.url.path}/{request.query_params}"
        incache=False
        #incache= cache_service.get(cache_key)
        if incache and not nocache:
            logger.debug(f"{cache_key} cached ({settings.redis_cache_expiration})s")
            payload=json.loads(incache)
        else:
            payload=await func(*args, **kwargs)
            #cache_service.set(cache_key, json.dumps(payload))
            #cache_service.expire(cache_key,settings.redis_cache_expiration)
        logger.debug(f"{cache_key} elapsed Time: {time.time()-start}")
        return payload
    return wrapper


def check_apikey(key:str):
    if key != settings.api_key :
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
