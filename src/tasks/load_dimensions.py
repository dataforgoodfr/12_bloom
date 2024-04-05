import sys

from bloom.logger import logger
from tasks.base import BaseTask
from tasks.dimensions import LoadDimPortFromCsv, LoadDimVesselFromCsv, LoadDimZoneAmpFromCsv,\
                             ComputePortGeometryBuffer

import hashlib
from datetime import datetime



class LoadDimensions(BaseTask):

    def run(self, *args, **kwargs):
        LoadDimZoneAmpFromCsv(*args, **kwargs).start()
        ComputePortGeometryBuffer(*args, **kwargs).start()
        LoadDimPortFromCsv(*args, **kwargs).start()
        LoadDimVesselFromCsv(*args, **kwargs).start()

    def on_error(self, *args, **kwargs):
        logger.error("LoadDimensions::on_error")
        logger.error(f"batch:{kwargs['batch']}")
        pass


if __name__ == "__main__":
    task = LoadDimensions(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0),
                          **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()
