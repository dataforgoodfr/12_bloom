import sys
from tasks.base import BaseTask
from bloom.config import settings
import logging
from bloom.logger import logger
from tasks.transformations import  (
                                    ComputePortGeometryBuffer,
                                    UpdateVesselDataVoyage
                                    )

class PipelinePorts(BaseTask):
    
    def run(self,*args,**kwargs):
        ComputePortGeometryBuffer(*args,**kwargs).start()
        UpdateVesselDataVoyage(*args,**kwargs).start()


if __name__ == "__main__":
    task= PipelinePorts(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0 ),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()