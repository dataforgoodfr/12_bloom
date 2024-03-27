import sys
from tasks.base import BaseTask
from bloom.config import settings
import logging
from bloom.logger import logger
from tasks.dimensions import LoadDimZoneAmpFromCsv,LoadDimPortFromCsv,LoadDimVesselFromCsv

class LoadDimensions(BaseTask):
    
    def run(self,*args,**kwargs):
        LoadDimZoneAmpFromCsv(*args,**kwargs).start()
        LoadDimPortFromCsv(*args,**kwargs).start()
        LoadDimVesselFromCsv(*args,**kwargs).start()


if __name__ == "__main__":
    task= LoadDimensions(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0 ),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()