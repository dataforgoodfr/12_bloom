from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from geoalchemy2 import Geometry
from bloom.config import settings
from bloom.container import UseCases
from bloom.config import settings
from bloom.container import UseCases
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey,cache)
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, select
router = APIRouter()
from bloom.infra.database.database_manager import Base
from geoalchemy2.shape import to_shape
from typing_extensions import Annotated
from bloom.routers.requests import (
    PaginatedResult,
    RangeHeader,
    RangeHeaderParser
)
from sqlalchemy.dialects.postgresql import JSONB


class Zone(Base):
    __tablename__ = "mart_dim_zones"
    __table_args__ = {"schema": "marts"}

    id = Column("id", Integer, primary_key=True)
    category = Column("category", String)
    sub_category = Column("sub_category", String)
    name = Column("name", String, nullable=False)
    geometry = Column("geometry", Geometry(geometry_type="GEOMETRY", srid=settings.srid))
    centroid = Column("centroid", Geometry(geometry_type="POINT", srid=settings.srid))
    json_data = Column("json_data", JSONB)
    created_at = Column("created_at", DateTime(timezone=True))
    enable = Column("enable",Boolean(), server_default="True")

class ZoneCategory(Base):
    __tablename__ = "mart_dim_zones__categories"
    __table_args__ = {"schema": "marts"}

    category = Column("category", String, primary_key=True)
    sub_category = Column("sub_category", String, primary_key=True)

class ZoneSummary(Base):
    __tablename__ = "mart_dim_zones__summary"
    __table_args__ = {"schema": "marts"}

    id = Column("id", Integer, primary_key=True)
    category = Column("category", String)
    sub_category = Column("sub_category", String)
    name = Column("name", String, nullable=False)
    created_at = Column("created_at", DateTime(timezone=True))

@router.get("/zones")
#@cache
async def list_zones(request: Request,
                     nocache: bool = False,
                     key: str = Depends(X_API_KEY_HEADER),
                     range: Annotated[RangeHeader, Depends(RangeHeaderParser)] = None):
    check_apikey(key)
    print(f"Range:{range}")
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        payload = []
        if range is not None:
            base_query = session.query(Zone, func.count().over().label('total'))
            total_query = session.query(func.count().label('total')).select_from(Zone)
            total_count = session.execute(total_query).scalar_one_or_none()
            for i, spec in enumerate(range.spec):
                paginated = base_query
                if spec.start != None: paginated = paginated.offset(spec.start)
                if spec.end != None and spec.start != None: paginated = paginated.limit(spec.end + 1 - spec.start)
                if spec.end != None and spec.start == None: paginated = paginated.offset(total_count - spec.end).limit(
                    spec.end)
                results = session.execute(paginated).all()
                total = results[0][1] if len(results) > 0 else 0

                payload.extend([{
                    "id": model[0].id,
                    "category": model[0].category,
                    "sub_category": model[0].sub_category,
                    "name": model[0].name,
                    "geometry": to_shape(model[0].geometry).__geo_interface__ if model[0].geometry else None,
                    "centroid": to_shape(model[0].centroid).__geo_interface__ if model[0].centroid else None,
                    "json_data": model[0].json_data,
                    "created_at": model[0].created_at,
                    "enable": model[0].enable
                } for model in results])
                if spec.end == None: range.spec[i].end = total - 1
        else:
            payload = [{
                "id": model.id,
                "category": model.category,
                "sub_category": model.sub_category,
                "name": model.name,
                "geometry": to_shape(model.geometry).__geo_interface__ if model.geometry else None,
                "centroid": to_shape(model.centroid).__geo_interface__ if model.centroid else None,
                "json_data": model.json_data,
                "created_at": model.created_at,
                "enable": model.enable
            } for model in session.execute(session.query(Zone)).scalars()]

        response = JSONResponse(content=jsonable_encoder(payload),
                            status_code=206 if range is not None else 200)
        if range is not None:
            for s in range.spec:
                response.headers.append(key='Content-Range',
                                        value=f"{s.start if s.start != None else ''}-{s.end if s.end != None else ''}/{total}")

        return response

    
@router.get("/zones/categories")
@cache
async def list_zone_categories(request: Request, nocache: bool = False, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(ZoneCategory)
        return session.execute(stmt).scalars().all()
    
@router.get("/zones/summary")
@cache
async def list_zones_summary_test(request: Request,
                             nocache: bool = False,
                             key: str = Depends(X_API_KEY_HEADER),
                             ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        print("Coucou")
        stmt = select(ZoneSummary)
        return session.execute(stmt).scalars().all()


@router.get("/zones/{zone_id}")
# @cache
async def get_zone(request: Request, zone_id: int, nocache: bool = False, key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
            stmt = select(Zone).where(Zone.id == zone_id)
            res = session.execute(stmt).scalars().first()

            if res:
                return {
                    "id": res.id,
                    "category": res.category,
                    "sub_category": res.sub_category,
                    "name": res.name,
                    "geometry": to_shape(res.geometry).__geo_interface__ if res.geometry else None,
                    "centroid": to_shape(res.centroid).__geo_interface__ if res.centroid else None,
                    "json_data": res.json_data,
                    "created_at": res.created_at,
                    "enable": res.enable
                }

            return res if res else None