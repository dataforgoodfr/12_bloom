from bloom.logger import logger

import hashlib
from datetime import datetime

class BaseTask():
    args = None
    kwargs = None
    _stop_on_error: bool = True

    @property
    def stop_on_error(self) -> bool:
        return self._stop_on_error

    @stop_on_error.setter
    def stop_on_error(self, value: bool) -> None:
        self._stop_on_error = value

    def __init__(self, *args, **kwargs):
        if 'batch' not in kwargs:
            kwargs['batch']=datetime.now().strftime(f"{self.__class__.__name__}-%y%m%d%H%M%S%f")
        self.args = args
        self.kwargs = kwargs

    def start(self) -> None:
        logger.info(f"Starting task {self.__class__.__name__}")
        try:
            self.run(*self.args, **self.kwargs)
            logger.info(f"Task {self.__class__.__name__} sucess")
            self.on_success(*self.args, **self.kwargs)
        except Exception as e:
            logger.error(f"Task {self} did not finished correctly. {e}")
            self.on_error(*self.args, **self.kwargs)
            raise(e)
            #if self.stop_on_error:
            #    exit(e.args[0])
            #else:
            #    raise (e)

    def run(self, *args, **kwargs) -> None:
        logger.info(f"Task {self.__class__.__name__} success")
        pass

    def on_success(self,*args, **kwargs) -> None:
        logger.info(f"Task {self.__class__.__name__} success")
        pass

    def on_error(self,*args, **kwargs) -> None:
        logger.error(f"Task {self.__class__.__name__} on_error")
        pass

    def stop(self) -> None:
        pass
