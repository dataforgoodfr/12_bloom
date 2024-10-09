from pydantic import BaseModel
from typing import Generic,TypeVar, List
from typing_extensions import Annotated, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
import redis
from pydantic.generics import GenericModel
from bloom.config import settings


rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)


