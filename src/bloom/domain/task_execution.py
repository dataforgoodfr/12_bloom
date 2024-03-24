from datetime import datetime
from typing import Union

from pydantic import BaseModel


class TaskExecution(BaseModel):
    name: str
    point_in_time: datetime
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
