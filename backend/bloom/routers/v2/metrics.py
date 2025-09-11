from bloom.routers.v2.vessels import timedelta_to_iso8601
from fastapi import APIRouter, Depends, Request
from geoalchemy2 import Geometry
import redis
from bloom.config import settings
from bloom.container import UseCases
from typing_extensions import Optional
from sqlalchemy import ARRAY, Column, Date, DateTime, Float, Integer, Interval, String, and_, asc, case, desc, lateral, select, func, true
from bloom.infra.database.database_manager import Base
from bloom.routers.requests import CachedRequest, DatetimeRangeRequest, OrderByEnum,OrderByRequest,PageParams
from bloom.dependencies import ( X_API_KEY_HEADER, cache, check_apikey)
from geoalchemy2.shape import to_shape



router = APIRouter()
rd = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

class VesselTimeByZoneResponse(Base):
    __tablename__ = "mart_metrics__detailed_visits"
    __table_args__ = {'schema': 'marts'}

    day_date = Column("day_date", Date, primary_key=True)
    zone_id = Column("zone_id", String, primary_key=True)
    category = Column("category", String)
    sub_category = Column("sub_category", String)
    name = Column("name", String)
    zone_created_at = Column("zone_created_at", DateTime(timezone=True))
    centroid = Column("centroid", Geometry(geometry_type="POINT", srid=settings.srid))
    vessel_id = Column("vessel_id", String, primary_key=True)
    mmsi = Column("mmsi", Integer)
    ship_name = Column("ship_name", String)
    length = Column("length", Float)
    country_iso3 = Column("country_iso3", String)
    type = Column("type", String)
    imo = Column("imo", String)
    ircs = Column("ircs", String)
    vessel_created_at = Column("vessel_created_at", DateTime(timezone=True))
    zone_visiting_duration = Column("zone_visiting_duration", Interval)
    created_at = Column("created_at", DateTime(timezone=True))

class VesselSummaryActivityResponse(Base):
    __tablename__ = "mart_metrics__zones_category_visited"
    __table_args__ = {'schema': 'marts'}

    day_date = Column("day_date", Date, primary_key=True)
    vessel_id = Column("vessel_id", String, primary_key=True)
    mmsi = Column("mmsi", Integer)
    ship_name = Column("ship_name", String)
    length = Column("length", Float)
    country_iso3 = Column("country_iso3", String)
    type = Column("type", String)
    imo = Column("imo", String)
    ircs = Column("ircs", String)
    time_in_amp_zone = Column("time_in_amp_zone", Interval)
    time_in_territorial_waters = Column("time_in_territorial_waters", Interval)
    time_in_zone_with_no_fishing_rights = Column("time_in_zone_with_no_fishing_rights", Interval)
    created_at = Column("created_at", DateTime(timezone=True))

class VesselCountInMPAResponse(Base):
    __tablename__ = "mart_metrics__mpas_activity"
    __table_args__ = {'schema': 'marts'}

    day_date = Column("day_date", Date, primary_key=True)
    vessel_ids = Column("vessel_ids", ARRAY(String))
    zones_ids = Column("zones_ids", ARRAY(String))
    count_vessels = Column("count_vessels", Integer)
    count_zones = Column("count_zones", Integer)
    created_at = Column("created_at", DateTime(timezone=True))

class VesselCountResponse(Base):
    __tablename__ = "mart_metrics__vessels_at_sea"
    __table_args__ = {'schema': 'marts'}

    day_date = Column("day_date", Date, primary_key=True)
    vessel_ids = Column("vessel_ids", ARRAY(String))
    count_vessels_at_sea = Column("count_vessels_at_sea", Integer)
    created_at = Column("created_at", DateTime(timezone=True))

@router.get("/metrics/vessels/time-by-zone")
# @cache
async def read_metrics_all_vessels_visiting_time_by_zone(request: Request,
                                            vessel_id: Optional[str] = None,
                                            category: Optional[str] = None,
                                            sub_category: Optional[str] = None,
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            pagination: PageParams = Depends(),
                                            order: OrderByRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()

    print(datetime_range)

    with db.session() as session:
        stmt = select(VesselTimeByZoneResponse.vessel_id.label("vessel_id"),
                      VesselTimeByZoneResponse.zone_id.label("zone_id"),
                      VesselTimeByZoneResponse.category.label("category"),
                      VesselTimeByZoneResponse.sub_category.label("sub_category"),
                      VesselTimeByZoneResponse.name.label("name"),
                      VesselTimeByZoneResponse.zone_created_at.label("zone_created_at"),
                      VesselTimeByZoneResponse.centroid.label("centroid"),
                      VesselTimeByZoneResponse.mmsi.label("mmsi"),
                      VesselTimeByZoneResponse.ship_name.label("ship_name"),
                      VesselTimeByZoneResponse.length.label("length"),
                      VesselTimeByZoneResponse.country_iso3.label("country_iso3"),
                      VesselTimeByZoneResponse.type.label("type"),
                      VesselTimeByZoneResponse.imo.label("imo"),
                      VesselTimeByZoneResponse.ircs.label("ircs"),
                      VesselTimeByZoneResponse.vessel_created_at.label("vessel_created_at"),
                      func.sum(VesselTimeByZoneResponse.zone_visiting_duration).label("vessel_visiting_time_by_zone")
                      ).where(
                VesselTimeByZoneResponse.day_date.between(datetime_range.start_at, datetime_range.end_at)
        ).group_by(
            VesselTimeByZoneResponse.vessel_id,
            VesselTimeByZoneResponse.zone_id,
            VesselTimeByZoneResponse.category,
            VesselTimeByZoneResponse.sub_category,
            VesselTimeByZoneResponse.name,
            VesselTimeByZoneResponse.zone_created_at,
            VesselTimeByZoneResponse.centroid,
            VesselTimeByZoneResponse.mmsi,
            VesselTimeByZoneResponse.ship_name,
            VesselTimeByZoneResponse.length,
            VesselTimeByZoneResponse.country_iso3,
            VesselTimeByZoneResponse.type,
            VesselTimeByZoneResponse.imo,
            VesselTimeByZoneResponse.ircs,
            VesselTimeByZoneResponse.vessel_created_at,
        )

        if category:
                stmt = stmt.where(VesselTimeByZoneResponse.category == category)
        if sub_category:
            stmt = stmt.where(VesselTimeByZoneResponse.sub_category == sub_category)
        stmt =  stmt.order_by(func.sum(VesselTimeByZoneResponse.zone_visiting_duration).asc())\
            if  order.order == OrderByEnum.ascending \
            else stmt.order_by(func.sum(VesselTimeByZoneResponse.zone_visiting_duration).desc())

        stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
        stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
        
        if vessel_id is not None:
            stmt=stmt.where(VesselTimeByZoneResponse.vessel_id==vessel_id)
        
        res = session.execute(stmt).all()

        json_data = [
            {
                "zone": {
                    "id": row.zone_id,
                    "created_at": row.zone_created_at,
                    "category": row.category,
                    "sub_category": row.sub_category,
                    "name": row.name,
                    "centroid": to_shape(row.centroid).__geo_interface__ if row.centroid else None
                },
                "vessel": {
                    "id": row.vessel_id,
                    "mmsi": row.mmsi,
                    "imo": row.imo,
                    "ship_name": row.ship_name,
                    "width": None,
                    "length": row.length,
                    "country_iso3": row.country_iso3,
                    "type": row.type,
                    "ircs": row.ircs,
                    "created_at": row.vessel_created_at,
                },
                "vessel_visiting_time_by_zone": timedelta_to_iso8601(row.vessel_visiting_time_by_zone)
            }
            for row in res
        ]

        return json_data

@router.get("/metrics/vessels-count-in-mpas")
@cache
async def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:

        if datetime_range.start_at == datetime_range.end_at:
            stmt = select(VesselCountInMPAResponse.count_vessels).where(
                VesselCountInMPAResponse.day_date == datetime_range.start_at
            )

            return session.execute(stmt).first()
        
        # Step 1: Define the unnest as a lateral subquery
        unnest_alias = lateral(
            select(func.unnest(VesselCountInMPAResponse.vessel_ids).label("vessel_id"))
        ).alias("unnest_alias")

        # Step 2: Build the main query
        stmt = (
            select(func.count(func.distinct(unnest_alias.c.vessel_id)))
            .select_from(VesselCountInMPAResponse)
            .join(unnest_alias, true())  # cross join lateral
            .where(
                VesselCountInMPAResponse.day_date.between(
                    datetime_range.start_at,
                    datetime_range.end_at,
                )
            )
        )

        return session.execute(stmt).scalars().first()

@router.get("/metrics/mpas-visited")
@cache
async def read_metrics_mpas_visited_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:

        if datetime_range.start_at == datetime_range.end_at:
            stmt = select(VesselCountInMPAResponse.count_zones).where(
                VesselCountInMPAResponse.day_date == datetime_range.start_at
            )

            return session.execute(stmt).first()
        
        # Step 1: Define the unnest as a lateral subquery
        unnest_alias = lateral(
            select(func.unnest(VesselCountInMPAResponse.zones_ids).label("zone_id"))
        ).alias("unnest_alias")

        # Step 2: Build the main query
        stmt = (
            select(func.count(func.distinct(unnest_alias.c.zone_id)))
            .select_from(VesselCountInMPAResponse)
            .join(unnest_alias, true())  # cross join lateral
            .where(
                VesselCountInMPAResponse.day_date.between(
                    datetime_range.start_at,
                    datetime_range.end_at,
                )
            )
        )

        return session.execute(stmt).scalars().first()
    
@router.get("/metrics/vessels-at-sea")
@cache
async def read_metrics_vessels_at_sea_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:

        if datetime_range.start_at.date() == datetime_range.end_at.date():
            stmt = select(VesselCountResponse.count_vessels_at_sea).where(
                VesselCountResponse.day_date == datetime_range.start_at
            )

            return session.execute(stmt).scalars().first()

        unnest_alias = (select(func.unnest(VesselCountResponse.vessel_ids).label("vessel_id"))
            .where(VesselCountResponse.day_date.between(
                    datetime_range.start_at,
                    datetime_range.end_at,
                ))
        )

        stmt = select(func.count(unnest_alias.c.vessel_id.distinct())).select_from(unnest_alias)

        return session.execute(stmt).scalars().first()
    

@router.get("/metrics/vessels/activity")
@cache
async def read_metrics_vessels_in_activity_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           category: Optional[str] = None,
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(
                    VesselSummaryActivityResponse.vessel_id,
                    VesselSummaryActivityResponse.mmsi,
                    VesselSummaryActivityResponse.ship_name,
                    VesselSummaryActivityResponse.length,
                    VesselSummaryActivityResponse.country_iso3,
                    VesselSummaryActivityResponse.type,
                    VesselSummaryActivityResponse.imo,
                    VesselSummaryActivityResponse.ircs,
                    func.sum(VesselSummaryActivityResponse.time_in_amp_zone if category == 'amp' 
                             else (VesselSummaryActivityResponse.time_in_territorial_waters if category == 'Territorial waters' else 
                                   VesselSummaryActivityResponse.time_in_zone_with_no_fishing_rights)).label("total_time_in_category"),
                ).where(
                VesselSummaryActivityResponse.day_date.between(datetime_range.start_at, datetime_range.end_at)
        ).group_by(
            VesselSummaryActivityResponse.vessel_id,
            VesselSummaryActivityResponse.mmsi,
            VesselSummaryActivityResponse.ship_name,
            VesselSummaryActivityResponse.length,
            VesselSummaryActivityResponse.country_iso3,
            VesselSummaryActivityResponse.type,
            VesselSummaryActivityResponse.imo,
            VesselSummaryActivityResponse.ircs,
        )
        
        stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
        stmt =  stmt.order_by(asc("total_time_in_category"))\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(desc("total_time_in_category"))
        stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt

        result = session.execute(stmt).all()

        metrics = []
        for res in result:
            metrics.append({
                "vessel": {
                    "id": res[0],
                    "mmsi": res[1],
                    "ship_name": res[2],
                    "length": res[3],
                    "country_iso3": res[4],
                    "type": res[5],
                    "imo": res[6],
                    "ircs": res[7],
                },
                "total_time_in_category": timedelta_to_iso8601(res[8]),
            })

        return metrics
    

@router.get("/metrics/zones/activity")
@cache
async def read_metrics_zones_visited_total(request: Request,
                                           datetime_range: DatetimeRangeRequest = Depends(),
                                           pagination: PageParams = Depends(),
                                           order: OrderByRequest = Depends(),
                                           category: Optional[str] = None,
                                           caching: CachedRequest = Depends(),
                                           key: str = Depends(X_API_KEY_HEADER),
                                           ):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = (
            select(VesselTimeByZoneResponse.zone_id,
                   VesselTimeByZoneResponse.category,
                   VesselTimeByZoneResponse.sub_category,
                   VesselTimeByZoneResponse.name,
                   VesselTimeByZoneResponse.zone_created_at,
                   VesselTimeByZoneResponse.centroid,
                   func.sum(VesselTimeByZoneResponse.zone_visiting_duration).label("total_duration"))
            .where(VesselTimeByZoneResponse.day_date
                .between(datetime_range.start_at, datetime_range.end_at))
            .group_by(VesselTimeByZoneResponse.zone_id,
            VesselTimeByZoneResponse.category,
            VesselTimeByZoneResponse.sub_category,
            VesselTimeByZoneResponse.name,
            VesselTimeByZoneResponse.zone_created_at,
            VesselTimeByZoneResponse.centroid)
        )

        if category:
            stmt = stmt.where(VesselTimeByZoneResponse.category == category)

        stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
        stmt =  stmt.order_by(asc("total_duration"))\
            if  order.order == OrderByEnum.ascending \
            else stmt.order_by(desc("total_duration"))
        stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt


        result = session.execute(stmt).all()

        metrics = []

        for res in result:
            metrics.append(
                {
                    "zone": {
                        "id": res[0],
                        "category": res[1],
                        "sub_category": res[2],
                        "name": res[3],
                        "created_at": res[4],
                        "centroid": to_shape(res[5]).__geo_interface__ if res[5] is not None else None,
                    },
                    "total_visit_duration": timedelta_to_iso8601(res[6]),
                }
            )

        return metrics
    

@router.get("/metrics/zones/{zone_id}/visiting-time-by-vessel")
@cache
async def read_metrics_zone_visiting_time_by_vessel(request: Request,
                                            zone_id: str,
                                            datetime_range: DatetimeRangeRequest = Depends(),
                                            pagination: PageParams = Depends(),
                                            order: OrderByRequest = Depends(),
                                            caching: CachedRequest = Depends(),
                                            key: str = Depends(X_API_KEY_HEADER),):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = (
            select(VesselTimeByZoneResponse.zone_id,
                   VesselTimeByZoneResponse.category,
                   VesselTimeByZoneResponse.sub_category,
                   VesselTimeByZoneResponse.name,
                   VesselTimeByZoneResponse.zone_created_at,
                   VesselTimeByZoneResponse.centroid,
                   VesselTimeByZoneResponse.vessel_id,
                   VesselTimeByZoneResponse.mmsi,
                   VesselTimeByZoneResponse.ship_name,
                   VesselTimeByZoneResponse.length,
                   VesselTimeByZoneResponse.country_iso3,
                   VesselTimeByZoneResponse.type,
                   VesselTimeByZoneResponse.imo,
                   VesselTimeByZoneResponse.ircs,
                   VesselTimeByZoneResponse.vessel_created_at,
                   func.sum(VesselTimeByZoneResponse.zone_visiting_duration).label("vessel_visiting_time_by_zone")
               ).where(
                   and_(VesselTimeByZoneResponse.zone_id == zone_id),
                   VesselTimeByZoneResponse.day_date.between(datetime_range.start_at, datetime_range.end_at)
               ).group_by(
                    VesselTimeByZoneResponse.vessel_id,
                    VesselTimeByZoneResponse.zone_id,
                    VesselTimeByZoneResponse.category,
                    VesselTimeByZoneResponse.sub_category,
                    VesselTimeByZoneResponse.name,
                    VesselTimeByZoneResponse.zone_created_at,
                    VesselTimeByZoneResponse.centroid,
                    VesselTimeByZoneResponse.mmsi,
                    VesselTimeByZoneResponse.ship_name,
                    VesselTimeByZoneResponse.length,
                    VesselTimeByZoneResponse.country_iso3,
                    VesselTimeByZoneResponse.type,
                    VesselTimeByZoneResponse.imo,
                    VesselTimeByZoneResponse.ircs,
                    VesselTimeByZoneResponse.vessel_created_at,
            )
        )

        stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
        stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
        stmt =  stmt.order_by(asc("vessel_visiting_time_by_zone"))\
            if  order.order == OrderByEnum.ascending \
            else stmt.order_by(desc("vessel_visiting_time_by_zone"))

        result = session.execute(stmt).all()

        metrics = []

        for res in result:
            metrics.append({
                "zone": {
                    "id": res[0],
                    "category": res[1],
                    "sub_category": res[2],
                    "name": res[3],
                    "created_at": res[4],
                    "centroid": to_shape(res[5]).__geo_interface__ if res[5] is not None else None
                },
                "vessel": {
                    "id": res[6],
                    "mmsi": res[7],
                    "ship_name": res[8],
                    "width": None,
                    "length": res[9],
                    "country_iso3": res[10],
                    "type": res[11],
                    "imo": res[12],
                    "ircs": res[13],
                    "created_at": res[14],
                },
                "vessel_visiting_time_by_zone": timedelta_to_iso8601(res[15])
            })

        return metrics