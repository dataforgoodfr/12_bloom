from tasks.base import BaseTask
from tasks.data import LoadAmpDataTask, LoadPortDataTask, LoadVesselsDataTask, LoadVesselPositionsDataTask
from bloom.config import settings
import logging

logging.basicConfig()
logging.getLogger("bloom.tasks").setLevel(settings.logging_level)

class InitTask(BaseTask):
    
    def run(self):
    
        LoadAmpDataTask().start()
        LoadPortDataTask().start()
        LoadVesselsDataTask().start()
        LoadVesselPositionsDataTask().start()


if __name__ == "__main__":
    task= InitTask()
    task.start()