import sys
from tasks.base import BaseTask
from bloom.config import settings
import logging
from bloom.logger import logger
from tasks.data import LoadAmpDataTask, LoadPortDataTask, LoadVesselsDataTask

class LoadDimensions(BaseTask):
    
    def run(self,*args,**kwargs):
        LoadAmpDataTask(*args,**kwargs).start()
        LoadPortDataTask(*args,**kwargs).start()
        LoadVesselsDataTask(*args,**kwargs).start()


if __name__ == "__main__":
    task= LoadDimensions(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0 ),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()