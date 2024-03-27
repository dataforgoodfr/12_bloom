from abc import ABC, abstractmethod
from typing import Any
from typing_extensions import Self

import logging
from bloom.config import settings
from bloom.logger import logger

class BaseTask():
    args=None
    kwargs=None
    _stop_on_error:bool=True
    
    @property
    def stop_on_error(self) -> bool:
        return self._stop_on_error
    
    @stop_on_error.setter
    def stop_on_error(self, value:bool) -> None:
        self._stop_on_error=value
    
    def __init__(self,*args,**kwargs):
        self.args=args
        self.kwargs=kwargs
    
    def start(self) -> None:
        logger.info(f"Starting task {self.__class__.__name__}")
        try:
            self.run(*self.args,**self.kwargs)
            logger.info(f"Task {self.__class__.__name__} finished")
        except Exception as e:
            logger.error(f"Task {self} did not finished correctly. {e}")
            if self.stop_on_error:
                exit(e.args[0])
            else:
                raise(e)
            
    def run(self,*args,**kwargs) ->None:
        pass
    def stop(self) -> None:
        pass