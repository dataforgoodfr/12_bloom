from fastapi import Request, HTTPException, Depends, Header
from starlette.background import BackgroundTask
from typing import Annotated, Any, Type,Callable
from bloom.config import settings
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict
from functools import wraps
import time
import json
import re
from bloom.logger import logger
from sqlalchemy.sql.expression import func
## Reference for pagination design
## https://jayhawk24.hashnode.dev/how-to-implement-pagination-in-fastapi-feat-sqlalchemy
X_API_KEY_HEADER=APIKeyHeader(name="x-key")

from fastapi.encoders import jsonable_encoder
from typing import Generic, Mapping,TypeVar, List
from typing import Optional
from sqlalchemy.orm import Session, Query

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def UsingCacheQuery(cache:Annotated[Optional[bool|None],Header()] = None):
    return True if cache else False

def CacheKey(request:Request):
    return f"{request.url}/{request.query_params}#{request.headers}"


def RangeHeaderParser(range:Annotated[Optional[str|None],Header()] = None):
    return RangeHeader(range) if range is not None else None

class RangeSpec(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

class RangeSet(BaseModel):
    specs: list[RangeSpec] = []

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
            self.specs.append(spec)
    unit: str = 'item'

TYPE=TypeVar('RETURN')
REPOSITORY=TypeVar('REPOSITORY')

class PaginatedSqlResult(BaseModel,Generic[TYPE]):
    """ Permet de réaliser uen requête paginée sur la base
        Paramètres en entrée:
        - session:Session = session SqlAlchemy pour réaliser la query
        - query:Query = Query initiale sur laquelle appliquer la pagination
        - range:RangeSet = (Optionel) Liste des plages de pagination
        - map_to_domain:Callback = fonction de conversion SqlModel=>PydanticSchema (Ex: ZoneRepository.map_to_domain)
        - unit:str = Unité de pagination (seul "items" est pris en charge)
        Cette classe renvoie
        - items:list[TYPE] = liste des items format pydantic soit complète si range est null, soit correspondantes au plages demandées via range
        - total:int = nombre total d'items hors pagination
    """
    model_config= ConfigDict(
                    arbitrary_types_allowed=True)
    def __init__(self,
                 *args,**kwargs):
        super().__init__(*args,**kwargs)
        total_query=self.query.add_column(func.count().over().label('total'))
        self.items=[]
        if self.range is not None:
            for i, spec in enumerate(self.range.specs):
                paginated=total_query
                if spec.start != None: paginated = paginated.offset(spec.start)
                if spec.end != None and spec.start != None: paginated = paginated.limit(spec.end + 1 - spec.start)
                if spec.end != None and spec.start == None: paginated = paginated.offset(total_count - spec.end).limit(
                    spec.end)
                results = self.session.execute(paginated).all()
                self.items.extend([json.loads(self.map_to_domain(model[0]).model_dump_json()) for model in results])
                if len(results) > 0:
                    self.total = results[0][-1]
        else:
            result=self.session.execute(total_query).all()
            total_count=0
            if len(result) > 0:
                total_count = result[0][-1]
            self.items = [ json.loads(self.map_to_domain(row[0]).model_dump_json()) for row in result]
    session: Session
    query: Query
    map_to_domain: Callable
    range: Optional[RangeSet]=None
    unit: Optional[str|None] = None
    items: Optional[TYPE]=None
    total: Optional[int|None]= None

class PaginatedJSONResponse(JSONResponse):
    """ Génère une réponse de type JSONResponse paginée au standard PostgREST
        Paramètres en entrée:
        - result:PaginatedSqlResult = object de type PaginatedResult issue d'une précédente requête
        - request:Request = object de type Request, issue du routeur FastAPI
        Cette classe renvoie
        - status_code 200 OK si result.range est vide
        - status_code 206 Partiel si result.range n'est pas vide accompagné de headers
        Content-Range et de heander Link next/previous pour chaque Range présentes
        dans le result.range
    """
    def __init__(self, result:PaginatedSqlResult, request:Request) -> None:
        status_code=200
        if len(result.items) != result.total:
            status_code=206
        super().__init__(content=result.items,
                         status_code=status_code)
        if result.range is not None:
            self_header=""
            self_next_header=""
            self_previous_header=""
            for spec in result.range.specs:
                self_header=f"{self_header}{'' if len(self_header) == 0 else ',' }{spec.start}-{spec.end}"

                next_start=spec.end+1
                next_end=2*spec.end-spec.start+1
                if next_end > result.total: next_end=result.total
                if next_start < result.total:
                    self_next_header=f"{self_next_header}{'' if len(self_next_header) == 0 else ',' }{next_start}-{next_end}"
                
                previous_start=2*spec.start-1-spec.end
                previous_end=spec.start-1
                if previous_start < 0 : previous_start=0
                if previous_end >= previous_start:
                    self_previous_header=f"{self_previous_header}{'' if len(self_previous_header) == 0 else ',' }{previous_start}-{previous_end}"
                self.headers.append(key='Content-Range',
                                    value=f"{spec.start if spec.start != None else ''}-{spec.end if spec.end != None else ''}/{result.total}")
                #if spec.end-spec.start > 0:
                #    self.headers.append(key='Link',value=f"<{request.url}>; range=\"{spec.end+1}-{2*spec.end-spec.start}\"; rel=\"next\"")
                #    self.headers.append(key='Link',value=f"<{request.url}>; range=\"{spec.end+1}-{2*spec.end-spec.start}\"; rel=\"previous\"")
            self.headers.append(key='Link',value=f"<{request.url}>; range=\"{self_next_header}\"; rel=\"next\"")
            self.headers.append(key='Link',value=f"<{request.url}>; range=\"{self_previous_header}\"; rel=\"previous\"")
            for spec in result.range.specs:
                size=spec.end-spec.start
                self.headers.append(key='Link',value=f"<{request.url}>; range=\"{self_header}\"; rel=\"self\"")

def check_apikey(key:str):
    if key != settings.api_key :
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
