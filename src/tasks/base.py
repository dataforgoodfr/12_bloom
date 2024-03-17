from abc import ABC, abstractmethod
from typing import Any
from typing_extensions import Self

import logging
from bloom.config import settings

logging.basicConfig()
logging.getLogger("bloom.tasks").setLevel(settings.logging_level)

class BaseTask():
    @property
    def parent(self) -> Self:
        return self._parent
    @parent.setter
    def parent(self,parent:Self):
        self._parent=parent
    def add(self, task:Self) -> None:
        pass
    def remove(self, task:Self) -> None:
        pass
    def is_group(self) -> bool:
        return False
    pass
    
    def start(self):
        logger=logging.getLogger("bloom.tasks")
        logger.setLevel(settings.logging_level)
        logger.info(f"Starting task {self.__class__.__name__}")
        logger.debug(f"Starting task {self}")
        try:
            self.run()
            logger.info(f"Task {self.__class__.__name__} finished")
            logger.debug(f"Task {self} finished")
        except Exception as e:
            logger.error(f"Task {self} did not finished correctly. {e}")
            raise(e)
    def run(self):
        pass
    def stop(self):
        pass