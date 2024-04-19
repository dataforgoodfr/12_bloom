import sys

from tasks.base import BaseTask
from tasks.facts import CleanPositionsTask, LoadSpireDataFromApi
from tasks.transformations import UpdateVesselDataVoyage


class PipelinePorts(BaseTask):

    def run(self, *args, **kwargs):
        UpdateVesselDataVoyage(*args, **kwargs).start()
        CleanPositionsTask(*args, **kwargs).start()


if __name__ == "__main__":
    task = PipelinePorts(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0),
                         **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()
