from bloom.infra.database.database_manager import Base
from fastapi import APIRouter, Depends, Request
from geoalchemy2 import Geometry
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from bloom.routers.requests import CachedRequest
from bloom.dependencies import ( X_API_KEY_HEADER,check_apikey,cache)
from bloom.config import settings
from bloom.domain.port import PostListView
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, select
from geoalchemy2.shape import to_shape

router = APIRouter()

class Port(Base):
    __tablename__ = "mart_dim_ports"
    __table_args__ = {"schema": "marts"}

    id = Column("id", String, primary_key=True)
    name = Column("name", String)
    locode = Column("locode", String)
    url = Column("url", String)
    country_iso3 = Column("country_iso3", String)
    latitude = Column("latitude", Float)
    longitude = Column("longitude", Float)
    geometry_point = Column("geometry_point", Geometry(geometry_type="POINT", srid=settings.srid))
    has_excursion = Column("has_excursion", Boolean)
    created_at = Column("created_at", DateTime(timezone=True))
    updated_at = Column("updated_at", DateTime(timezone=True))

@router.get("/ports")
@cache
async def list_ports(request:Request,
                        caching: CachedRequest = Depends(),
                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(Port)
        res =  session.execute(stmt).scalars()
        ports = []
        for pos in res:
            port = {
                "id": pos.id,
                "name": pos.name,
                "locode": pos.locode,
                "url": pos.url,
                "country_iso3": pos.country_iso3,
                "latitude": pos.latitude,
                "longitude": pos.longitude,
                "geometry_point": to_shape(pos.geometry_point).__geo_interface__ if pos.geometry_point is not None else None,
                "has_excursion": pos.has_excursion,
                "created_at": pos.created_at,
                "updated_at": pos.updated_at
            }
            ports.append(port)
        return ports

@router.get("/ports/{port_id}")
@cache
async def get_port(request: Request, 
                   port_id: str,
                   key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(Port).where(Port.id == port_id)
        res =  session.execute(stmt).scalars().first()
        port = {
            "id": res.id,
            "name": res.name,
            "locode": res.locode,
            "url": res.url,
            "country_iso3": res.country_iso3,
            "latitude": res.latitude,
            "longitude": res.longitude,
            "geometry_point": to_shape(res.geometry_point).__geo_interface__ if res.geometry_point is not None else None,
            "has_excursion": res.has_excursion,
            "created_at": res.created_at,
            "updated_at": res.updated_at
        }
        return port if port else None