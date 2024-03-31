import sys

from tasks.base import BaseTask
from tasks.load_dimensions import LoadDimensions
from tasks.load_facts import LoadFacts
from bloom.config import settings
from bloom.logger import logger
from bloom.config import settings

class InitTask(BaseTask):
    
    def run(self,*args,**kwargs):
        
        args={
            'port_data_csv_path': settings.port_data_csv_path,
            'amp_data_csv_path': settings.amp_data_csv_path,
            'vessel_data_csv_path': settings.vessel_data_csv_path,
        }
        kwargs={**args, **kwargs}
        LoadDimensions(*args,**kwargs).start()
        LoadFacts(*args,**kwargs).start()


if __name__ == "__main__":
    task= InitTask(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0 ),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()