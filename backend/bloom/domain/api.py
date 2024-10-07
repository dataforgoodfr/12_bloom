from fastapi import Request, HTTPException
from pydantic import BaseModel, ConfigDict, Field,conint
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic.generics import GenericModel
from fastapi.security import APIKeyHeader
from bloom.config import settings

## Reference for pagination design
## https://jayhawk24.hashnode.dev/how-to-implement-pagination-in-fastapi-feat-sqlalchemy
X_API_KEY_HEADER=APIKeyHeader(name="x-key")

class CachedRequest(BaseModel):
    nocache:bool=False

def check_apikey(key:str):
    if key != settings.api_key :
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class DatetimeRangeRequest(BaseModel):
    start_at: datetime = datetime.now()-timedelta(days=7)
    end_at: datetime = datetime.now()

class OrderByEnum(str, Enum):
    ascending = "ASC"
    descending = "DESC"

class OrderByRequest(BaseModel):
    order: OrderByEnum = OrderByEnum.ascending

class PaginatedRequest(BaseModel):
    offset: int|None = 0
    limit: int|None = 100
    order_by: OrderByRequest = OrderByEnum.ascending


class PageParams(BaseModel):
    """ Request query params for paginated API. """
    offset: conint(ge=0) = 0
    limit: conint(ge=1, le=1000) = 100

T = TypeVar("T")

class PagedResponseSchema(GenericModel,Generic[T]):
    total: int
    limit: int
    offset: int
    next: str|None
    previous: str|None
    results: List[T]

def paginate(request: Request, page_params: PageParams, query, ResponseSchema: BaseModel) -> PagedResponseSchema[T]:
    """Paginate the query."""

    print(f"{request.url.scheme}://{request.client}/{request.url.path}")
    paginated_query = query.offset((page_params.offset) * page_params.limit).limit(page_params.limit).all()

    return PagedResponseSchema(
        total=query.count(),
        offset=page_params.offset,
        limit=page_params.limit,
        next="",
        previous="",
        results=[ResponseSchema.from_orm(item) for item in paginated_query],
    )