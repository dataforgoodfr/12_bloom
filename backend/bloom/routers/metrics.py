from fastapi import APIRouter, Depends, Query
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal
from datetime import datetime

router = APIRouter()
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, db=0)

@router.get("/metrics/vessels-in-activity/total", tags=['metrics'])
def read_metrics_vessels_in_activity_total(start_at: datetime, end_at: datetime = None):
    pass

@router.get("/metrics/zone-visited/total", tags=['metrics'])
def read_metrics_vessels_in_activity_total(start_at: datetime, end_at: datetime = None):
    pass

@router.get("/metrics/vessels/{vessel_id}/visits/{visit_type}", tags=['metrics'])
def read_metrics_vessels_visits_by_visit_type(
        vessel_id: int,
        visit_type: str,
        start_at: datetime,
        end_at: datetime = None,
        limit: int = 10,
        orderBy: str = 'DESC'):
    pass