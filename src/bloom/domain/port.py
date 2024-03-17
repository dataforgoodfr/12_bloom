from datetime import datetime

from pydantic import BaseModel, ConfigDict
from shapely import Point, Polygon


class Port(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int | None = None
    name: str
    locode: str
    url: str | None = None
    country_iso3: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geometry_point: Point | None = None
    geometry_buffer: Polygon | None = None
    has_excursion: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
