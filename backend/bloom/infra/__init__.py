import abc
from typing_extensions import Self
from dependency_injector.providers import Callable
from bloom.infra.repositories.repository_vessel import VesselRepositoryInterface

class UnitOfWorkInterface(abc.ABC):
    repository_vessel: VesselRepositoryInterface

    @abc.abstractmethod
    def __enter__(self) -> Self:
        raise NotImplementedError()

    @abc.abstractmethod
    def __exit__(self, *args) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError()
    
class UnitOfWork(UnitOfWorkInterface):
    def __init__(self,
                 session_factory:Callable,
                 vessel_repository_factory:Callable):
        self._session_factory=session_factory
        self._repository_vessel_factory=vessel_repository_factory
        
    def __enter__(self) -> Self:
        with self._session_factory() as session:
            self._session = session
            self.repository_vessel=self._repository_vessel_factory(session=self._session)
    
        return self

    def __exit__(self, *args) -> None:
        self._session.rollback()
        self._session.close()
    
    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()