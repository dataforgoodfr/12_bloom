from pydantic import BaseModel, Field,conint, ConfigDict
from fastapi import Request
from datetime import datetime, timedelta
from enum import Enum
from typing import Generic,TypeVar, List
from typing import Optional, Annotated
from fastapi import Header

import re

class OrderByEnum(str, Enum):
    ascending = "ASC"
    descending = "DESC"

class DatetimeRangeRequest(BaseModel):
    start_at: datetime = Field(default=datetime.now()-timedelta(days=7))
    end_at: datetime = datetime.now()

class OrderByRequest(BaseModel):
    order: OrderByEnum = OrderByEnum.ascending

class PaginatedRequest(BaseModel):
    offset: int|None = 0
    limit: int|None = 100
    order_by: OrderByRequest = OrderByEnum.ascending


class PageParams(BaseModel):
    """ Request query params for paginated API. """
    offset: conint(ge=0) = 0
    limit: conint(ge=1, le=100000) = 100

T = TypeVar("T")

class PagedResponseSchema(BaseModel,Generic[T]):
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