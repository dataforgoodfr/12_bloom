from contextlib import AbstractContextManager
from dataclasses import dataclass
from abc import ABC, abstractmethod
from bloom.infra.repositories import AbstractRepository
from bloom.infra.repositories.repository_vessel import VesselRepository

from dependency_injector.providers import Callable

from bloom.infra.repositories.repository_vessel import VesselRepository


class AbstractUnitOfWork(AbstractContextManager):
    excursion_repository: AbstractRepository
    metrics_repository: AbstractRepository
    port_repository: AbstractRepository
    rel_segment_zone_repository: AbstractRepository
    segment_repository: AbstractRepository
    spire_ais_data_repository: AbstractRepository
    task_execution_repository: AbstractRepository
    vessel_repository: VesselRepository
    zone_repository: AbstractRepository

    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self,session_factory:Callable):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.vessel_repository = VesselRepository(self.session)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def __exit__(self,exc_type,exc_value,traceback):
        if exc_type:
            self.rollback()
        self.session.close()
