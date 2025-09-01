from fastapi import APIRouter, Depends, Request
from geoalchemy2 import Geometry
from redis import Redis
from bloom.config import settings
from bloom.container import UseCases
from typing import Any, Optional
import json
from bloom.config import settings
from bloom.container import UseCases
from bloom.logger import logger
from bloom.routers.requests import DatetimeRangeRequest,OrderByRequest,PageParams
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey,cache)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, select, text
router = APIRouter()
from bloom.infra.database.database_manager import Base
from geoalchemy2.shape import to_shape

class Vessel(Base):
    __tablename__ = "mart_dim_vessels"  
    __table_args__ = {"schema": "marts"}

    vessel_id = Column("id", String, primary_key=True)
    mmsi = Column("mmsi", Integer)
    ship_name = Column("ship_name", String)
    width = Column("width", String)
    length = Column("length", Float)
    type = Column("type", String)
    length_class = Column("length_class", String)
    country_iso3 = Column("country_iso3", String)
    imo = Column("imo", Integer)
    cfr = Column("cfr", String)
    ircs = Column("ircs", String)
    external_marking = Column("external_marking", String)
    tracking_activated = Column("tracking_activated", Boolean)
    tracking_status = Column("tracking_status", String)
    home_port_id = Column("home_port_id", Integer)
    created_at = Column("created_at", DateTime(timezone=True), nullable=False)
    updated_at = Column("updated_at", DateTime(timezone=True))
    check = Column("check", String)

class VesselType(Base):
    __tablename__ = "mart_dim_vessels__types"
    __table_args__ = {"schema": "marts"}

    type = Column("type", String, primary_key=True)

class VesselClass(Base):
    __tablename__ = "mart_dim_vessels__classes"
    __table_args__ = {"schema": "marts"}

    length_class = Column("length_class", String, primary_key=True)

class VesselCountry(Base):
    __tablename__ = "mart_dim_vessels__countries"
    __table_args__ = {"schema": "marts"}

    country_iso3 = Column("country_iso3", String, primary_key=True)

class VesselPosition(Base):
    __tablename__ = "mart_dim_vessels__last_positions"
    __table_args__ = {"schema": "marts"}
    
    vessel_id = Column("vessel_id", String, primary_key=True)
    mmsi = Column("mmsi", Integer)
    ship_name = Column("ship_name", String)
    width = Column("width", String)
    length = Column("length", Float)
    country_iso3 = Column("country_iso3", String)
    type = Column("type", String)
    imo = Column("imo", Integer)
    cfr = Column("cfr", String)
    external_marking = Column("external_marking", String)
    ircs = Column("ircs", String)
    tracking_activated = Column("tracking_activated", Boolean)
    tracking_status = Column("tracking_status", String)
    home_port_id = Column("home_port_id", Integer)
    vessel_created_at = Column("vessel_created_at", DateTime(timezone=True), nullable=False)
    vessel_updated_at = Column("vessel_updated_at", DateTime(timezone=True))
    check = Column("check", String)
    length_class = Column("length_class", String)
    excursion_id = Column("excursion_id", String)
    position = Column("position", Geometry(geometry_type="POINT", srid=settings.srid))
    timestamp = Column("timestamp", DateTime(timezone=True), nullable=False)
    heading = Column("heading", Float)
    speed = Column("speed", Float)
    arrival_port_id = Column("arrival_port_id", Integer)


@router.get("/vessels/types")
async def list_vessel_types(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselType.type)
        return session.execute(stmt).scalars().all()
    
@router.get("/vessels/classes")
async def list_vessel_classes(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselClass.length_class)
        return session.execute(stmt).scalars().all()

@router.get("/vessels/countries")
async def list_vessel_countries(request: Request, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselCountry.country_iso3)
        return session.execute(stmt).scalars().all()


@router.get("/vessels")
async def list_vessels(request: Request, # used by @cache
                       nocache:bool=False, # used by @cache
                       key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(Vessel)
        return session.execute(stmt).scalars().all()

@router.get("/vessels/{vessel_id}")
async def get_vessel(request: Request, # used by @cache
                     vessel_id: str,
                     nocache:bool=False, # used by @cache
                     key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(Vessel).where(Vessel.vessel_id == vessel_id)
        return session.execute(stmt).scalars().first()


@router.get("/vessels/all/positions/last")
async def list_all_vessel_last_position(request: Request, # used by @cache
                                        nocache:bool=False, # used by @cache
                                        key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselPosition)
        res = session.execute(stmt).scalars()
        positions = []
        for pos in res:
            pos.position = to_shape(pos.position).__geo_interface__ if pos and pos.position else None
            positions.append(pos)
        return positions
    
@router.get("/vessels/{vessel_id}/positions/last")
async def get_vessel_last_position(request: Request, # used by @cache
                                   vessel_id: str,
                                   nocache:bool=False, # used by @cache
                                   key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselPosition).where(VesselPosition.vessel_id == vessel_id)
        res = session.execute(stmt).scalars().first()
        if res:
            res.position = to_shape(res.position).__geo_interface__ if res.position else None
        return res
    

