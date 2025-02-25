from datetime import datetime
from typing import Union

from bloom.infra.database import sql_model
from pydantic import BaseModel, ConfigDict


class PositionUpdate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    id: Union[int, None] = None
    vessel_id: int
    point_in_time: datetime | None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    @staticmethod
    def from_model(entity: sql_model.PositionUpdate):
        return PositionUpdate(
            id=entity.id,
            vessel_id=entity.vessel_id,
            point_in_time=entity.point_in_time,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
