from fastapi import APIRouter, Depends, Request
from geoalchemy2 import Geometry
from bloom.config import settings
from bloom.container import UseCases
from bloom.config import settings
from bloom.container import UseCases
from bloom.routers.requests import DatetimeRangeRequest, OrderByEnum,OrderByRequest,PageParams
from bloom.dependencies import (X_API_KEY_HEADER,check_apikey,cache)
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, Interval, String, and_, asc, desc, func, select
router = APIRouter()
from bloom.infra.database.database_manager import Base
from geoalchemy2.shape import to_shape
from timedelta_isoformat import timedelta
from datetime import timedelta

class Vessel(Base):
    __tablename__ = "mart_dim_vessels"  
    __table_args__ = {"schema": "marts"}

    id = Column("id", String, primary_key=True)
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

class VesselTrackedCount(Base):
    __tablename__ = "mart_dim_vessels__trackedcount"
    __table_args__ = {"schema": "marts"}

    count = Column("count", Integer, primary_key=True)
    updated_at = Column("updated_at", DateTime(timezone=True))

class VesselExcursionDay(Base):
    __tablename__ = "mart_dim_vessels__excursions_by_date"
    __table_args__ = {"schema": "marts"}

    excursion_id = Column("excursion_id", String, primary_key=True)
    day_excursion_date = Column("day_excursion_date", DateTime(timezone=True), primary_key=True)
    vessel_id = Column("vessel_id", String)
    departure_port_id = Column("departure_port_id", Integer)
    arrival_port_id = Column("arrival_port_id", Integer)
    departure_at = Column("departure_at", DateTime(timezone=True))
    arrival_at = Column("arrival_at", DateTime(timezone=True))
    total_time_at_sea = Column("total_time_at_sea", Interval)
    total_time_in_amp = Column("total_time_in_amp", Interval)
    total_time_default_ais = Column("total_time_default_ais", Interval)
    total_time_in_territorial_waters = Column("total_time_in_territorial_waters", Interval)
    total_time_in_zones_with_no_fishing_rights = Column("total_time_in_zones_with_no_fishing_rights", Interval)
    total_time_fishing = Column("total_time_fishing", Interval)
    total_time_fishing_in_amp = Column("total_time_fishing_in_amp", Interval)
    total_time_fishing_in_zones_with_no_fishing_rights = Column("total_time_fishing_in_zones_with_no_fishing_rights", Interval)
    total_time_fishing_in_territorial_waters = Column("total_time_fishing_in_territorial_waters", Interval)
    excursion_created_at = Column("excursion_created_at", DateTime(timezone=True))

class Segment(Base):
    __tablename__ = "mart_dim_vessels__segments_by_excursion_ids"
    __table_args__ = {"schema": "marts"}

    excursion_id = Column("excursion_id", String, primary_key=True)
    vessel_id = Column("vessel_id", String)
    daysegments_date = Column("daysegments_date", DateTime(timezone=True))
    timestamp_start = Column("timestamp_start", DateTime(timezone=True), primary_key=True)
    timestamp_end = Column("timestamp_end", DateTime(timezone=True))
    segment_duration = Column("segment_duration", Interval)
    start_position = Column("start_position", Geometry(geometry_type="POINT", srid=settings.srid))
    end_position = Column("end_position", Geometry(geometry_type="POINT", srid=settings.srid))
    average_speed = Column("average_speed", Float)
    course_at_start = Column("course_at_start", Float)
    course_at_end = Column("course_at_end", Float)
    speed_at_start = Column("speed_at_start", Float)
    speed_at_end = Column("speed_at_end", Float)
    heading_at_start = Column("heading_at_start", Float)
    heading_at_end = Column("heading_at_end", Float)
    segment_type = Column("segment_type", String)
    in_amp_zone = Column("in_amp_zone", Boolean)
    in_territorial_waters = Column("in_territorial_waters", Boolean)
    in_zones_with_no_fishing_rights = Column("in_zones_with_no_fishing_rights", Boolean)
    created_at = Column("created_at", DateTime(timezone=True))


def timedelta_to_iso8601(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    if total_seconds == 0:
        return "PT0S"

    days, remainder = divmod(total_seconds, 86400)  # 1 jour = 86400s
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = ["P"]

    if days:
        parts.append(f"{days}D")

    if hours or minutes or seconds:
        parts.append("T")
        if hours:
            parts.append(f"{hours}H")
        if minutes:
            parts.append(f"{minutes}M")
        if seconds:
            parts.append(f"{seconds}S")

    return "".join(parts)

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
    
@router.get("/vessels/tracked-count")
async def get_vessel_tracked_number(key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(VesselTrackedCount.count)
        return session.execute(stmt).scalars().first()



@router.get("/vessels")
@cache
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
@cache
async def get_vessel(request: Request, # used by @cache
                     vessel_id: str,
                     nocache:bool=False, # used by @cache
                     key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = select(Vessel).where(Vessel.id == vessel_id)
        return session.execute(stmt).scalars().first()


@router.get("/vessels/all/positions/last")
@cache
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
            position = {
                "arrival_port_id": pos.arrival_port_id,
                "excursion_id": pos.excursion_id,
                "heading": pos.heading,
                "position": to_shape(pos.position).__geo_interface__ if pos and pos.position else None,
                "speed": pos.speed,
                "timestamp": pos.timestamp,
                "vessel": {
                    "id": pos.vessel_id,
                    "mmsi": pos.mmsi,
                    "ship_name": pos.ship_name,
                    "width": pos.width,
                    "length": pos.length,
                    "country_iso3": pos.country_iso3,
                    "type": pos.type,
                    "imo": pos.imo,
                    "cfr": pos.cfr, 
                    "external_marking": pos.external_marking,
                    "ircs": pos.ircs,
                    "length_class": pos.length_class
                }
            }
            positions.append(position)
        return positions
    
@router.get("/vessels/{vessel_id}/positions/last")
@cache
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
            position = {
                "arrival_port_id": res.arrival_port_id,
                "excursion_id": res.excursion_id,
                "heading": res.heading,
                "position": to_shape(res.position).__geo_interface__ if res and res.position else None,
                "speed": res.speed,
                "timestamp": res.timestamp,
                "vessel": {
                    "id": res.vessel_id,
                    "mmsi": res.mmsi,
                    "ship_name": res.ship_name,
                    "width": res.width,
                    "length": res.length,
                    "country_iso3": res.country_iso3,
                    "type": res.type,
                    "imo": res.imo,
                    "cfr": res.cfr,
                    "external_marking": res.external_marking,
                    "ircs": res.ircs,
                    "length_class": res.length_class
                }
            }
        return position if res else None

@router.get("/vessels/{vessel_id}/excursions")
@cache
async def list_vessel_excursions(request: Request, # used by @cache
                                vessel_id: str,
                                nocache:bool=False, # used by @cache
                                datetime_range: DatetimeRangeRequest= Depends(),
                                pagination: PageParams = Depends(),
                                order: OrderByRequest = Depends(),
                                key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt_total = (
            select(
                VesselExcursionDay.vessel_id,
                func.sum(VesselExcursionDay.total_time_at_sea).label("total_time_at_sea"),
                func.sum(VesselExcursionDay.total_time_in_amp).label("total_time_in_amp"),
                func.sum(VesselExcursionDay.total_time_default_ais).label("total_time_default_ais"),
                func.sum(VesselExcursionDay.total_time_in_territorial_waters).label("total_time_in_territorial_waters"),
                func.sum(VesselExcursionDay.total_time_in_zones_with_no_fishing_rights).label("total_time_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing).label("total_time_fishing"),
                func.sum(VesselExcursionDay.total_time_fishing_in_amp).label("total_time_fishing_in_amp"),
                func.sum(VesselExcursionDay.total_time_fishing_in_zones_with_no_fishing_rights).label("total_time_fishing_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing_in_territorial_waters).label("total_time_fishing_in_territorial_waters"),
            )
            .where(and_(VesselExcursionDay.vessel_id == vessel_id, VesselExcursionDay.day_excursion_date.between(datetime_range.start_at, datetime_range.end_at)))
        ).group_by(VesselExcursionDay.vessel_id)

        total = session.execute(stmt_total).first()

        stmt = (
            select(
                VesselExcursionDay.excursion_id,
                VesselExcursionDay.vessel_id,
                VesselExcursionDay.departure_port_id,
                VesselExcursionDay.arrival_port_id,
                VesselExcursionDay.departure_at,
                VesselExcursionDay.arrival_at,
                func.sum(VesselExcursionDay.total_time_at_sea).label("total_time_at_sea"),
                func.sum(VesselExcursionDay.total_time_in_amp).label("total_time_in_amp"),
                func.sum(VesselExcursionDay.total_time_default_ais).label("total_time_default_ais"),
                func.sum(VesselExcursionDay.total_time_in_territorial_waters).label("total_time_in_territorial_waters"),
                func.sum(VesselExcursionDay.total_time_in_zones_with_no_fishing_rights).label("total_time_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing).label("total_time_fishing"),
                func.sum(VesselExcursionDay.total_time_fishing_in_amp).label("total_time_fishing_in_amp"),
                func.sum(VesselExcursionDay.total_time_fishing_in_zones_with_no_fishing_rights).label("total_time_fishing_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing_in_territorial_waters).label("total_time_fishing_in_territorial_waters"),
                func.coalesce(VesselExcursionDay.excursion_created_at)
            )
            .where(and_(VesselExcursionDay.vessel_id == vessel_id, VesselExcursionDay.day_excursion_date.between(datetime_range.start_at, datetime_range.end_at)))
        ).group_by(VesselExcursionDay.excursion_id, 
                   VesselExcursionDay.vessel_id,
                   VesselExcursionDay.departure_port_id,
                   VesselExcursionDay.arrival_port_id,
                   VesselExcursionDay.departure_at,
                   VesselExcursionDay.arrival_at,
                   VesselExcursionDay.excursion_created_at)
        
        stmt =  stmt.order_by(asc(VesselExcursionDay.departure_at))\
                if  order.order == OrderByEnum.ascending \
                else stmt.order_by(desc(VesselExcursionDay.departure_at))
        
        result = [
            {
                "excursion_id": row[0],
                "vessel_id": row[1],
                "departure_port_id": row[2],
                "arrival_port_id": row[3],
                "departure_at": row[4],
                "arrival_at": row[5],
                "total_time_at_sea": timedelta_to_iso8601(row[6]),
                "total_time_in_amp": timedelta_to_iso8601(row[7]),
                "total_time_default_ais": timedelta_to_iso8601(row[8]) if row[8] else "PT0S",
                "total_time_in_territorial_waters": timedelta_to_iso8601(row[9]),
                "total_time_in_zones_with_no_fishing_rights": timedelta_to_iso8601(row[10]),
                "total_time_fishing": timedelta_to_iso8601(row[11]),
                "total_time_fishing_in_amp": timedelta_to_iso8601(row[12]),
                "total_time_fishing_in_zones_with_no_fishing_rights": timedelta_to_iso8601(row[13]),
                "total_time_fishing_in_territorial_waters": timedelta_to_iso8601(row[14]),
                "excursion_created_at": row[15],
            } for row in session.execute(stmt).all()]
                
        return {
            "vessel_id": total[0] if total[0] else vessel_id,
            "total_time_at_sea": timedelta_to_iso8601(total[1]) if total[1] else "PT0S",
            "total_time_in_amp": timedelta_to_iso8601(total[2]) if total[2] else "PT0S",
            "total_time_default_ais": timedelta_to_iso8601(total[3]) if total[3] else "PT0S",
            "total_time_in_territorial_waters": timedelta_to_iso8601(total[4]) if total[4] else "PT0S",
            "total_time_in_zones_with_no_fishing_rights": timedelta_to_iso8601(total[5]) if total[5] else "PT0S",
            "total_time_fishing": timedelta_to_iso8601(total[6]) if total[6] else "PT0S",
            "total_time_fishing_in_amp": timedelta_to_iso8601(total[7]) if total[7] else "PT0S",
            "total_time_fishing_in_zones_with_no_fishing_rights": timedelta_to_iso8601(total[8]) if total[8] else "PT0S",
            "total_time_fishing_in_territorial_waters": timedelta_to_iso8601(total[9]) if total[9] else "PT0S",
            "excursions" : result if result else [],
            "count": len(result),
        } if total else {
            "vessel_id": vessel_id,
            "total_time_at_sea": "PT0S",
            "total_time_in_amp": "PT0S",
            "total_time_default_ais": "PT0S",
            "total_time_in_territorial_waters": "PT0S",
            "total_time_in_zones_with_no_fishing_rights": "PT0S",
            "total_time_fishing": "PT0S",
            "total_time_fishing_in_amp": "PT0S",
            "total_time_fishing_in_zones_with_no_fishing_rights": "PT0S",
            "total_time_fishing_in_territorial_waters": "PT0S",
            "excursions" : [],
            "count": 0,
        }

@router.get("/vessels/{vessel_id}/excursions/{excursion_id}")
@cache
async def get_vessel_excursion(request: Request, # used by @cache
                               vessel_id: str,
                               excursion_id: str,
                               nocache:bool=False, # used by @cache
                               key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = (
            select(
                VesselExcursionDay.excursion_id,
                VesselExcursionDay.vessel_id,
                VesselExcursionDay.departure_port_id,
                VesselExcursionDay.arrival_port_id,
                VesselExcursionDay.departure_at,
                VesselExcursionDay.arrival_at,
                func.sum(VesselExcursionDay.total_time_at_sea).label("total_time_at_sea"),
                func.sum(VesselExcursionDay.total_time_in_amp).label("total_time_in_amp"),
                func.sum(VesselExcursionDay.total_time_default_ais).label("total_time_default_ais"),
                func.sum(VesselExcursionDay.total_time_in_territorial_waters).label("total_time_in_territorial_waters"),
                func.sum(VesselExcursionDay.total_time_in_zones_with_no_fishing_rights).label("total_time_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing).label("total_time_fishing"),
                func.sum(VesselExcursionDay.total_time_fishing_in_amp).label("total_time_fishing_in_amp"),
                func.sum(VesselExcursionDay.total_time_fishing_in_zones_with_no_fishing_rights).label("total_time_fishing_in_zones_with_no_fishing_rights"),
                func.sum(VesselExcursionDay.total_time_fishing_in_territorial_waters).label("total_time_fishing_in_territorial_waters"),
                func.coalesce(VesselExcursionDay.excursion_created_at)
            )
            .where(and_(VesselExcursionDay.vessel_id == vessel_id, VesselExcursionDay.excursion_id == excursion_id))
        ).group_by(VesselExcursionDay.excursion_id, 
                   VesselExcursionDay.vessel_id,
                   VesselExcursionDay.departure_port_id,
                   VesselExcursionDay.arrival_port_id,
                   VesselExcursionDay.departure_at,
                   VesselExcursionDay.arrival_at,
                   VesselExcursionDay.excursion_created_at)
        
        result = session.execute(stmt).first()

        json_data = {
                "excursion_id": result[0],
                "vessel_id": result[1],
                "departure_port_id": result[2],
                "arrival_port_id": result[3],
                "departure_at": result[4],
                "arrival_at": result[5],
                "total_time_at_sea": timedelta_to_iso8601(result[6]),
                "total_time_in_amp": timedelta_to_iso8601(result[7]),
                "total_time_default_ais": timedelta_to_iso8601(result[8]) if result[8] else "PT0S",
                "total_time_in_territorial_waters": timedelta_to_iso8601(result[9]),
                "total_time_in_zones_with_no_fishing_rights": timedelta_to_iso8601(result[10]),
                "total_time_fishing": timedelta_to_iso8601(result[11]),
                "total_time_fishing_in_amp": timedelta_to_iso8601(result[12]),
                "total_time_fishing_in_zones_with_no_fishing_rights": timedelta_to_iso8601(result[13]),
                "total_time_fishing_in_territorial_waters": timedelta_to_iso8601(result[14]),
                "excursion_created_at": result[15],
            }

    return json_data


@router.get("/vessels/{vessel_id}/excursions/{excursion_id}/segments")
@cache
async def list_vessel_excursion_segments(request: Request, # used by @cache
                                         vessel_id: str,
                                         excursion_id: str,
                                         nocache:bool=False, # used by @cache
                                         key: str = Depends(X_API_KEY_HEADER)):
    check_apikey(key)
    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        stmt = (
            select(Segment)
            .where(and_(Segment.vessel_id == vessel_id, Segment.excursion_id == excursion_id))
        )

        result = session.execute(stmt).scalars().all()

        json_data = [
            {
                "excursion_id": seg.excursion_id,
                "vessel_id": seg.vessel_id,
                "daysegments_date": seg.daysegments_date,
                "timestamp_start": seg.timestamp_start,
                "timestamp_end": seg.timestamp_end,
                "segment_duration": timedelta_to_iso8601(seg.segment_duration),
                "start_position": to_shape(seg.start_position).__geo_interface__ if seg and seg.start_position else None,
                "end_position": to_shape(seg.end_position).__geo_interface__ if seg and seg.end_position else None,
                "average_speed": seg.average_speed,
                "course_at_start": seg.course_at_start,
                "course_at_end": seg.course_at_end,
                "speed_at_start": seg.speed_at_start,
                "speed_at_end": seg.speed_at_end,
                "heading_at_start": seg.heading_at_start,
                "heading_at_end": seg.heading_at_end,
                "segment_type": seg.segment_type,
                "in_amp_zone": seg.in_amp_zone,
                "in_territorial_waters": seg.in_territorial_waters,
                "in_zones_with_no_fishing_rights": seg.in_zones_with_no_fishing_rights,
                "created_at": seg.created_at,
            }
            for seg in result
        ]

        return json_data