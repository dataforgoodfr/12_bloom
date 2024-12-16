from pydantic import BaseModel, Field
from contextlib import AbstractContextManager
from dependency_injector.providers import Callable
from sqlalchemy import select, func, and_, or_, text, literal_column, asc, desc, distinct
from bloom.infra.database import sql_model
from bloom.infra.database.database_manager import Base
from bloom.routers.requests import DatetimeRangeRequest,OrderByRequest,OrderByEnum, PageParams
from bloom.routers.requests import RangeHeader, PaginatedResult
from typing import Any, List, Union, Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from bloom.domain.vessel import Vessel,VesselListView
from bloom.domain.zone import Zone, ZoneListView
from bloom.infra.repositories.repository_vessel import VesselRepository
from bloom.infra.repositories.repository_zone import ZoneRepository
from bloom.domain.metrics import TotalTimeActivityTypeRequest

from bloom.domain.metrics import (
    ResponseMetricsVesselInActivitySchema,
    ResponseMetricsZoneVisitedSchema,
    ResponseMetricsVesselInZonesSchema,
    ResponseMetricsZoneVisitingTimeByVesselSchema,
    ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema,
    ResponseMetricsVesselVisitingTimeByZoneSchema,
)

class MetricsService():
    def __init__(
            self,
            session_factory: Callable,
    ) -> Callable[..., AbstractContextManager]:
        self.session_factory = session_factory

    def getVesselsInActivity(self,
                            datetime_range: DatetimeRangeRequest,
                            pagination: PageParams,
                            order: OrderByRequest):
        payload=[]
        with self.session_factory() as session:
            # Building request to get ativity time
            # activity is:
            #   arrival time in range start_at/end_at
            #   departure <= start_at and ( arrival == None or arrival >= end_at)
            stmt=select(sql_model.Vessel,
                        func.sum(sql_model.Segment.segment_duration).label("total_time_in_mpa")
                        )\
                .select_from(sql_model.Segment)\
                .join(sql_model.Excursion,sql_model.Segment.excursion_id==sql_model.Excursion.id)\
                .join(sql_model.Vessel,sql_model.Vessel.id ==sql_model.Excursion.vessel_id)\
                .where(
                    sql_model.Segment.in_amp_zone == True
                )\
                .where(
                        and_(
                            sql_model.Segment.timestamp_start <= datetime_range.end_at,
                            or_(sql_model.Segment.timestamp_end>= datetime_range.start_at,
                                sql_model.Segment.timestamp_end == None
                            )
                        )
                    )\
                .group_by(sql_model.Vessel)
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt =  stmt.order_by(asc("total_time_in_mpa"))\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(desc("total_time_in_mpa"))
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()
            # payload contains a list of sets(Vessel,datetime.timedelta)
            # here :
            #  item[0] is Vessel
            #  item[1] is total_time_at_sea
        return  [ResponseMetricsVesselInActivitySchema(
            vessel=VesselRepository.map_to_domain(item[0]).model_dump(),
            total_time_at_sea=item[1]
            )\
            for item in payload]

    def get_vessels_activity_in_zones(
        self,
        datetime_range: DatetimeRangeRequest,
        pagination: PageParams,
        order: OrderByRequest,
        category: Optional[str] = None,
    ):
        payload=[]
        with self.session_factory() as session:
            stmt = (
                select(
                   sql_model.Vessel,
                    func.sum(sql_model.Metrics.duration_total).label(
                        "total_time_in_zones"
                    ),
                )
                .select_from(sql_model.Metrics)
                .join(
                    sql_model.Vessel,
                    sql_model.Metrics.vessel_id == sql_model.Vessel.id,
                    isouter=True,
                )
                .where(
                    sql_model.Metrics.timestamp.between(
                        datetime_range.start_at, datetime_range.end_at
                    )
                )
                .group_by(
                    sql_model.Vessel
                )
            )
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            if category:
                stmt = stmt.where(sql_model.Zone.category == category)
            stmt = (
                stmt.order_by(asc("total_time_in_zones"))
                if order.order == OrderByEnum.ascending
                else stmt.order_by(desc("total_time_in_zones"))
            )
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()

        return [
            ResponseMetricsVesselInZonesSchema(
                vessel=VesselRepository.map_to_domain(item[0]).model_dump(),
                total_time_in_zones=item[1],
            )
            for item in payload
        ]

    def get_zones_visited(
        self,
        datetime_range: DatetimeRangeRequest,
        pagination: PageParams,
        order: OrderByRequest,
        category: Optional[str] = None,
    ):
        payload = []
        with self.session_factory() as session:
            stmt = (
                select(
                    sql_model.Zone,
                    func.sum(sql_model.Metrics.duration_total).label(
                        "visiting_duration"
                    ),
                )
                .select_from(sql_model.Metrics)
                .join(
                    sql_model.Zone,
                    sql_model.Zone.id == sql_model.Metrics.zone_id,
                )
                .where(
                    sql_model.Metrics.timestamp.between(
                        datetime_range.start_at, datetime_range.end_at
                    )
                )
                .where(sql_model.Metrics.zone_category == category)
                .group_by(sql_model.Zone)
            )
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            if category:
                stmt = stmt.where(sql_model.Zone.category == category)
            stmt = (
                stmt.order_by(asc("visiting_duration"))
                if order.order == OrderByEnum.ascending
                else stmt.order_by(desc("visiting_duration"))
            )
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload = session.execute(stmt).all()

        return [
            ResponseMetricsZoneVisitedSchema(
                zone=ZoneRepository.map_to_domain(item[0]).model_dump(),
                visiting_duration=item[1],
            )
            for item in payload
        ]

    def getVesselsAtSea(self,
                        datetime_range: DatetimeRangeRequest,
                        ):
        with self.session_factory() as session:
            stmt = (
                select(func.count(distinct(sql_model.Vessel.id)))
                .select_from(sql_model.Excursion)
                .join(
                    sql_model.Vessel,
                    sql_model.Excursion.vessel_id == sql_model.Vessel.id,
                )
                .where(
                    or_(
                        sql_model.Excursion.arrival_at.between(
                            datetime_range.start_at, datetime_range.end_at
                        ),
                        sql_model.Excursion.arrival_at == None,
                    )
                )
            )
        return session.execute(stmt).scalar()

    def getZoneVisited(self,
                        datetime_range: DatetimeRangeRequest,
                        pagination: PageParams,
                        order: OrderByRequest,
                        category: Optional[str]=None,
                        ):
        payload=[]
        with self.session_factory() as session:
            stmt=select(
                sql_model.Zone,
                func.sum(sql_model.Segment.segment_duration).label("visiting_duration")
                )\
                .select_from(sql_model.Zone)\
                .join(sql_model.RelSegmentZone,sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
                .join(sql_model.Segment,sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
                .where(
                        and_(
                            sql_model.Segment.timestamp_start <= datetime_range.end_at,
                            or_(sql_model.Segment.timestamp_end>= datetime_range.start_at,
                                sql_model.Segment.timestamp_end == None
                            )
                        )
                    )\
                .group_by(sql_model.Zone.id)
            if (category):
                stmt = stmt.where(sql_model.Zone.category == category)
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()
            # payload contains a list of sets(Zone,datetime.timedelta)
            # here :
            #  item[0] is Zone
            #  item[1] is visiting_duration
        return [ResponseMetricsZoneVisitedSchema(
            zone=ZoneRepository.map_to_domain(item[0]).model_dump(),
            visiting_duration=item[1]
            )\
            for item in payload]

    def getZoneVisitingTimeByVessel(self,
                                    zone_id: int,
                                    datetime_range: DatetimeRangeRequest,
                                    order: OrderByRequest,
                                    pagination: PageParams,):
        payload=[]
        with self.session_factory() as session:

            stmt=select(
                sql_model.Zone,
                sql_model.Vessel,
                func.sum(sql_model.Segment.segment_duration).label("zone_visiting_time_by_vessel")
            )\
            .select_from(sql_model.Zone)\
            .join(sql_model.RelSegmentZone, sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
            .join(sql_model.Segment, sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
            .join(sql_model.Excursion, sql_model.Excursion.id == sql_model.Segment.excursion_id)\
            .join(sql_model.Vessel, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
            .where(sql_model.Zone.id == zone_id)\
            .where(
                    and_(
                        sql_model.Segment.timestamp_start <= datetime_range.end_at,
                        or_(sql_model.Segment.timestamp_end>= datetime_range.start_at,
                            sql_model.Segment.timestamp_end == None
                        )
                    )
                )\
            .group_by(sql_model.Zone.id,sql_model.Vessel.id)

            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt

            payload=session.execute(stmt).all()
            # payload contains a list of sets(Zone,Vessel,datetime.timedelta)
            # here :
            #  item[0] is Zone
            #  item[1] is Vessel
            #  item[2] is visiting_duration
        return [ResponseMetricsZoneVisitingTimeByVesselSchema(
            zone=ZoneRepository.map_to_domain(item[0]).model_dump(),
            vessel=VesselRepository.map_to_domain(item[1]).model_dump(),
            zone_visiting_time_by_vessel=item[2]
            )\
            for item in payload]

    def getVesselVisitingTimeByZone(self,
                                    order: OrderByRequest,
                                    datetime_range: DatetimeRangeRequest,
                                    pagination: PageParams,
                                    vessel_id: int = None,
                                    category:Optional[str]=None,
                                    sub_category:Optional[str]=None,
                                    ):
        payload=[]
        with self.session_factory() as session:
            stmt=select(sql_model.Vessel,
                        sql_model.Zone,
                        func.sum(sql_model.Segment.segment_duration).label("vessel_visiting_time_by_zone")
                        )\
                .select_from(sql_model.Vessel)\
                .join(sql_model.Excursion, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
                .join(sql_model.Segment, sql_model.Segment.excursion_id == sql_model.Excursion.id)\
                .join(sql_model.RelSegmentZone, sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
                .join(sql_model.Zone, sql_model.Zone.id == sql_model.RelSegmentZone.zone_id)\
                .where(
                        and_(
                            sql_model.Segment.timestamp_start <= datetime_range.end_at,
                            or_(sql_model.Segment.timestamp_end>= datetime_range.start_at,
                                sql_model.Segment.timestamp_end == None
                            )
                        )
                    )\
                .group_by(sql_model.Vessel,
                        sql_model.Zone,)
            if category:
                stmt = stmt.where(sql_model.Zone.category == category)
            if sub_category:
                stmt = stmt.where(sql_model.Zone.sub_category == sub_category)
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                if  order.order == OrderByEnum.ascending \
                else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            if vessel_id is not None:
                stmt=stmt.where(sql_model.Vessel.id==vessel_id)

        return [ResponseMetricsVesselVisitingTimeByZoneSchema(
                    vessel=VesselListView(**VesselRepository.map_to_domain(model[0]).model_dump()),
                    zone=ZoneListView(**ZoneRepository.map_to_domain(model[1]).model_dump()),
                    vessel_visiting_time_by_zone=model[2]) for model in session.execute(stmt).all()]

    def getVesselVisitsByActivityType(self,
                                        vessel_id: int,
                                        activity_type: TotalTimeActivityTypeRequest,
                                        datetime_range: DatetimeRangeRequest):
        payload=[]
        with self.session_factory() as session:
            stmt=select(sql_model.Excursion.vessel_id,
                        literal_column(f"'{activity_type.type.value}'").label('activity'),
                        func.sum(sql_model.Excursion.total_time_at_sea).label("total_activity_time")
                        )\
                .select_from(sql_model.Excursion)\
                .where(sql_model.Excursion.vessel_id == vessel_id)\
                .where(
                        and_(
                            sql_model.Excursion.departure_at <= datetime_range.end_at,
                            or_(sql_model.Excursion.arrival_at>= datetime_range.start_at,
                                sql_model.Excursion.arrival_at == None
                            )
                        )
                    )\
                .group_by(sql_model.Excursion.vessel_id)\
                .union(select(
                    literal_column(vessel_id),
                    literal_column(f"'{activity_type.type.value}'"),
                    literal_column('0 seconds'),
                ))
            payload=session.execute(stmt.limit(1)).scalar_one_or_none()

        return [ ResponseMetricsVesselTotalTimeActivityByActivityTypeSchema(
                vessel_id=item.id,
                activity=item.activity,
                total_activity_time=item.total_activity_time,
                    ) for item in payload]
