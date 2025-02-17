import abc
from typing import Type, TypeVar, Generic, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql.expression import ScalarSelect, and_, or_

MODEL=TypeVar("MODEL")
DOMAIN=TypeVar("DOMAIN")

class RepositoryInterface(Generic[DOMAIN],abc.ABC):
    pass
    @abc.abstractmethod
    def get(self, **filters) -> list[DOMAIN]:
        raise NotImplementedError()
    @abc.abstractmethod
    def add(self, entities:list[DOMAIN]) -> None:
        raise NotImplementedError()
    @abc.abstractmethod
    def delete(self, entities:list[DOMAIN]) -> None:
        raise NotImplementedError()

class SqlBaseRepositoryMixIn(RepositoryInterface[DOMAIN],Generic[DOMAIN,MODEL],abc.ABC):
    def __init__(self,
            session: Session,
            model_cls: Type[MODEL],
            domain_cls: Type[DOMAIN]) -> None:
        self._session = session
        self._model_cls = model_cls
        self._domain_cls = domain_cls

    def _construct_list_stmt(self, offset=None, limit=None, **filters) -> ScalarSelect:
        stmt = select(self._model_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)
        
        if offset:
            stmt=stmt.offset(offset)
        if limit:
            stmt=stmt.limit(limit)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    def get(self,  offset=None, limit=None, **filters) -> list[DOMAIN]:
        stmt = self._construct_list_stmt(offset=offset,limit=limit,**filters)
        return [ self.map_model_to_domain(item) for item in self._session.execute(stmt).scalars()]
    
    def add(self,entities:list[DOMAIN]):
        stmt = self._construct_list_stmt()
        return self._session.execute(stmt)
    
    def delete(self, entities:list[DOMAIN]):
        stmt = self._construct_list_stmt()
        return self._session.execute(stmt)

    def map_model_to_domain(self,model:MODEL):
        return self._domain_cls(
            **model.__dict__
        )
    def map_domain_to_model(self,domain:DOMAIN):
        return self._model_cls(
            **{key:value for key,value in domain.__dict__.items() if key not in ['_sa_instance_state']}
        )