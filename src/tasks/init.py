import sys

from tasks.base import BaseTask
from tasks.load_dimensions import LoadDimensions
from tasks.load_facts import LoadFacts
from bloom.config import settings
from bloom.logger import logger

class InitTask(BaseTask):
    
    def run(self,*args,**kwargs):
    
        LoadDimensions(*args,**kwargs).start()
        LoadFacts(*args,**kwargs).start()


if __name__ == "__main__":
    task= InitTask(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0 ),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()