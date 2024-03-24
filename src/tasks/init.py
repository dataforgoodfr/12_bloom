from tasks.base import BaseTask
from tasks.data import LoadAmpDataTask, LoadPortDataTask, LoadVesselsDataTask, LoadVesselPositionsDataTask
from bloom.config import settings
from bloom.logger import logger

class InitTask(BaseTask):
    
    def run(self):
    
        LoadAmpDataTask().start()
        LoadPortDataTask().start()
        LoadVesselsDataTask().start()


if __name__ == "__main__":
    task= InitTask()
    task.start()