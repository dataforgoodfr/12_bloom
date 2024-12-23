from typing import TypeVar,Type,Generic, Optional, List, Any
from abc import ABC,abstractmethod
from sqlalchemy import select
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import ScalarSelect, and_, or_
from dependency_injector.providers import Callable

SCHEMA = TypeVar("SCHEMA", bound=BaseModel)
MODEL = TypeVar("MODEL", bound=Any)

class GenericRepository(Generic[SCHEMA], ABC):

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[SCHEMA]:
        raise NotImplementedError()

    @abstractmethod
    def list(self, **filters) -> List[SCHEMA]:
        raise NotImplementedError()

    @abstractmethod
    def add(self, record: SCHEMA) -> SCHEMA:
        raise NotImplementedError()
    
    @abstractmethod
    def add(self, records: List[SCHEMA]) -> List[SCHEMA]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, record: SCHEMA) -> SCHEMA:
        raise NotImplementedError()
    
    @abstractmethod
    def update(self, records: List[SCHEMA]) -> List[SCHEMA]:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError()
    
    def delete(self, ids: List[int]) -> None:
        raise NotImplementedError()

class GenericSqlRepository(GenericRepository[SCHEMA],Generic[SCHEMA,MODEL], ABC):
    def __init__(self,
            session: Session,
            model_cls: Type[MODEL],
            schema_cls: Type[SCHEMA]) -> None:
        self._session = session
        self._model_cls = model_cls
        self._schema_cls = model_cls

    def _construct_get_stmt(self, id: int) -> ScalarSelect:
        stmt = select(self._model_cls).where(self._model_cls.id == id)
        return stmt

    def get_by_id(self, id: int) -> Optional[SCHEMA]:
        stmt = self._construct_get_stmt(id)
        return self.map_to_domain(self._session.execute(stmt).scalar_one_or_none())

    def _construct_list_stmt(self, **filters) -> ScalarSelect:
        stmt = select(self._model_cls)
        where_clauses = []
        for c, v in filters.items():
            if not hasattr(self._model_cls, c):
                raise ValueError(f"Invalid column name {c}")
            where_clauses.append(getattr(self._model_cls, c) == v)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))
        return stmt

    def list(self, **filters) -> List[SCHEMA]:
        stmt = self._construct_list_stmt(**filters)
        return [ self.map_to_domain(item) for item in self._session.execute(stmt).scalars()]

    def add(self, record: SCHEMA) -> SCHEMA:
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return record
    
    def add(self, records: List[SCHEMA]) -> List[SCHEMA]:
        [self._session.add(record) for record in records]
        self._session.flush()
        self._session.refresh(records)
        return records

    def update(self, record: SCHEMA) -> SCHEMA:
        self._session.add(record)
        self._session.flush()
        self._session.refresh(record)
        return record
    
    def update(self, records: List[SCHEMA]) -> List[SCHEMA]:
        [self._session.add(record) for record in records]
        self._session.flush()
        self._session.refresh(records)
        return records

    def delete(self, id: int) -> None:
        record = self.get_by_id(id)
        if record is not None:
            self._session.delete(record)
            self._session.flush()
    
    def delete(self, ids: List[int]) -> None:
        for id in ids:
            record = self.get_by_id(id)
            if record is not None:
                self._session.delete(record)
        self._session.flush()
            
    
    @abstractmethod
    def map_to_domain(self,model: MODEL) -> SCHEMA:
        raise NotImplementedError()
    
    @abstractmethod
    def map_to_model(self,schema: SCHEMA) -> MODEL:
        raise NotImplementedError()