import abc
from typing import TypeVar, Generic, Optional, List
from datetime import datetime
from sqlalchemy.sql.expression import ScalarSelect, select, and_, or_, between

DOMAIN=TypeVar("DOMAIN")

class RepositoryError(Exception): ...
class ItemNotFoundError(RepositoryError): ...
class SCDRepositoryError(RepositoryError): ...
class SCDDateError(SCDRepositoryError): ...
class SCDDateStartEndInvertedError(SCDRepositoryError): ...
class SCDDateOverlapError(SCDRepositoryError): ...

class AbstractRepositoryClient():
    pass

def exclude_keys(d:dict,keys:list[str]):
    return {x: d[x] for x in d if x not in keys}

def construct_findBy_statement(model_type,
                             offset=None,
                             limit=None,
                             **filters,
                             )-> ScalarSelect:
    stmt = select(model_type)
    where_clauses = []
    for c, v in filters.items():
        print(c,v)
        if not hasattr(model_type, c):
            raise ValueError(f"Invalid column name {c}")
        where_clauses.append(getattr(model_type, c) == v)
    
    if offset:
        stmt=stmt.offset(offset)
    if limit:
        stmt=stmt.limit(limit)

    if len(where_clauses) == 1:
        stmt = stmt.where(where_clauses[0])
    elif len(where_clauses) > 1:
        stmt = stmt.where(and_(*where_clauses))
    return stmt

def construct_findBy_scd_statement(model_type,
                             offset:int=None,
                             limit:int=None,
                             scd_date:Optional[datetime]=None,
                             **filters)-> ScalarSelect:
    stmt = select(model_type)
    where_clauses = []
    for c, v in filters.items():
        if not hasattr(model_type, c):
            raise ValueError(f"Invalid column name {c}")
        where_clauses.append(getattr(model_type, c) == v)
    
    if offset:
        stmt=stmt.offset(offset)
    if limit:
        stmt=stmt.limit(limit)
    
    if scd_date != None:
        stmt=stmt.where(between(scd_date,model_type.scd_start, model_type.scd_end))
    else:
        stmt=stmt.where(model_type.scd_active == True)

    if len(where_clauses) == 1:
        stmt = stmt.where(where_clauses[0])
    elif len(where_clauses) > 1:
        stmt = stmt.where(and_(*where_clauses))
    return stmt

class AbstractRepository(abc.ABC, Generic[DOMAIN]):
    @abc.abstractmethod
    def findBy(self, offset=None, limit=None, **filters) -> List[DOMAIN]:
        raise NotImplementedError()
    """@abc.abstractmethod
    def insert(self, item:DOMAIN) -> DOMAIN:
        raise NotImplementedError()
    @abc.abstractmethod
    def update(self, item:DOMAIN) -> DOMAIN:
        raise NotImplementedError()
    @abc.abstractmethod
    def delete(self, filters:List) -> None:
        raise NotImplementedError()"""
    
class AbstractSqlAlchemyMixIn():
    pass
    
class AbstractScdRepositoryMixIn(Generic[DOMAIN]):
    @abc.abstractmethod
    def scd_insert(self,
                   item:DOMAIN,
                   scd_start:datetime,
                   scd_end:datetime) -> DOMAIN:
        """
        Insert new item with SCD date check.
        If date range in arguments overlaps existing date ranges then the
        function raise an error of type SCDDateOverlapError
        """
        raise NotImplementedError()
    @abc.abstractmethod
    def scd_update(self,
                   item:DOMAIN,
                   scd_start:datetime,
                   scd_end:datetime) -> DOMAIN:
        """
        update existing items with SCD date check.
        Item must already exist else raise an ItemNotFoundError error
        If date range in arguments overlaps existing date ranges, then
        existing date ranges are update in order to insert new date range
        """
        raise NotImplementedError()
    @abc.abstractmethod
    def scd_delete(self, item:DOMAIN) -> DOMAIN:
        raise NotImplementedError()