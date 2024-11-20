from pydantic import BaseModel, Field,conint
from fastapi import Request
from datetime import datetime, timedelta
from enum import Enum
from typing import Generic,TypeVar, List
from typing import Optional, Annotated
from fastapi import Header
import re


class RangeSpec(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

class RangeSet(BaseModel):
    spec: list[RangeSpec] = []

class RangeHeader(RangeSet):
    def __init__(self,value:str,*args,**kwargs):
        super().__init__(*args,**kwargs)
        match=re.search(r'^(items)=.*',value)
        if(match and len(match.groups())):
            self.unit = match.group(1)
        else:
            raise Exception("Range header bad format {value}. Expected '<unit:str='items'>=<start:int>-<end:int>,...")

        pattern=re.compile(r'((?P<start>\d*)-(?P<end>\d*))')
        for match in pattern.finditer(value):
            print(f"match:{match}")
            spec=RangeSpec()
            spec.start=int(match.group(2)) if match.group(2) else None
            spec.end=int(match.group(3)) if match.group(3) else None
            self.spec.append(spec)
    unit: str = 'item'


P=TypeVar('P')

class PaginatedResult(BaseModel,Generic[P]):
    unit: str
    spec: list[RangeSpec] = []
    payload: P
    total: int

class CachedRequest(BaseModel):
    nocache:bool=False


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
    
def RangeHeaderParser(range:Annotated[Optional[str|None],Header()] = None):
    return RangeHeader(range)


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