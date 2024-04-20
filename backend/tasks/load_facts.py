import sys

from tasks.base import BaseTask
from tasks.facts import CleanPositionsTask


class LoadFacts(BaseTask):

    def run(self, *args, **kwargs):
        CleanPositionsTask(*args, **kwargs).start()


if __name__ == "__main__":
    task = LoadFacts(*list(arg for arg in sys.argv[1:] if arg.find('=') <= 0),
                     **dict(arg.split('=') for arg in sys.argv[1:] if arg.find('=') > 0))
    task.start()
