from dataclasses import dataclass
from enum import Enum


@dataclass
class ErrorBase:
    code: Enum
    message: str


class DBErrorEnum(Enum):
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    DATA_ERROR = "DATA_ERROR"
    PROGRAMMING_ERROR = "PROGRAMMING_ERROR"


class DBError(ErrorBase):
    code: DBErrorEnum


class DBException(Exception):
    def __init__(self, error: DBError) -> None:
        self.error = error
