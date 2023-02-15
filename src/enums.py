from enum import Enum


class ExecutionMode(str, Enum):
    LOCAL = "local"
    CRONTAB = "crontab"
