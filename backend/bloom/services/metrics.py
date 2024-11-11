from pydantic import BaseModel, Field
from contextlib import AbstractContextManager
from dependency_injector.providers import Callable
from sqlalchemy import select, func, and_, or_, text, literal_column
from bloom.infra.database import sql_model
from bloom.infra.database.database_manager import Base
from bloom.routers.requests import DatetimeRangeRequest,OrderByRequest,OrderByEnum, PageParams

from bloom.domain.metrics import TotalTimeActivityTypeRequest


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
            stmt=select(sql_model.Vessel.id.label("vessel_id"),
                        sql_model.Vessel.mmsi.label("vessel_mmsi"),
                        sql_model.Vessel.ship_name.label("vessel_ship_name"),
                        sql_model.Vessel.width.label("vessel_width"),
                        sql_model.Vessel.length.label("vessel_length"),
                        sql_model.Vessel.country_iso3.label("vessel_country_iso3"),
                        sql_model.Vessel.type.label("vessel_type"),
                        sql_model.Vessel.imo.label("vessel_imo"),
                        sql_model.Vessel.cfr.label("vessel_cfr"),
                        sql_model.Vessel.external_marking.label("vessel_external_marking"),
                        sql_model.Vessel.ircs.label("vessel_ircs"),
                        sql_model.Vessel.home_port_id.label("vessel_home_port_id"),
                        sql_model.Vessel.details.label("vessel_details"),
                        sql_model.Vessel.tracking_activated.label("vessel_tracking_activated"),
                        sql_model.Vessel.tracking_status.label("vessel_tracking_status"),
                        sql_model.Vessel.length_class.label("vessel_length_class"),
                        sql_model.Vessel.check.label("vessel_check"),
                        func.sum(sql_model.Excursion.total_time_at_sea).label("total_time_at_sea")
                        )\
                .select_from(sql_model.Segment)\
                .join(sql_model.Excursion, sql_model.Segment.excursion_id == sql_model.Excursion.id)\
                .join(sql_model.Vessel, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
                .where(
                    or_(
                        sql_model.Excursion.arrival_at.between(datetime_range.start_at,datetime_range.end_at),
                        and_(sql_model.Excursion.departure_at <= datetime_range.end_at,
                            sql_model.Excursion.arrival_at == None))
                )\
                .group_by(sql_model.Vessel.id,sql_model.Excursion.total_time_at_sea)
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt =  stmt.order_by(sql_model.Excursion.total_time_at_sea.asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(sql_model.Excursion.total_time_at_sea.desc())
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()
        return payload
    
    def getZoneVisited(self,
                        datetime_range: DatetimeRangeRequest,
                        pagination: PageParams,
                        order: OrderByRequest):
        payload=[]
        with self.session_factory() as session:
            stmt=select(
                sql_model.Zone.id.label("zone_id"),
                sql_model.Zone.category.label("zone_category"),
                sql_model.Zone.sub_category.label("zone_sub_category"),
                sql_model.Zone.name.label("zone_name"),
                func.sum(sql_model.Segment.segment_duration).label("visiting_duration")
                )\
                .select_from(sql_model.Zone)\
                .join(sql_model.RelSegmentZone,sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
                .join(sql_model.Segment,sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
                .where(
                    or_(
                        sql_model.Segment.timestamp_start.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Segment.timestamp_end.between(datetime_range.start_at,datetime_range.end_at),)
                )\
                .group_by(sql_model.Zone.id)
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt
            payload=session.execute(stmt).all()
        return payload
    
    def getZoneVisitingTimeByVessel(self,
                                    zone_id: int,
                                    datetime_range: DatetimeRangeRequest,
                                    pagination: PageParams,
                                    order: OrderByRequest):
        payload=[]
        with self.session_factory() as session:
            
            stmt=select(
                sql_model.Zone.id.label("zone_id"),
                sql_model.Zone.category.label("zone_category"),
                sql_model.Zone.sub_category.label("zone_sub_category"),
                sql_model.Zone.name.label("zone_name"),
                sql_model.Vessel.id.label("vessel_id"),
                sql_model.Vessel.ship_name.label("vessel_name"),
                sql_model.Vessel.type.label("vessel_type"),
                sql_model.Vessel.length_class.label("vessel_length_class"),
                func.sum(sql_model.Segment.segment_duration).label("zone_visiting_time_by_vessel")
            )\
            .select_from(sql_model.Zone)\
            .join(sql_model.RelSegmentZone, sql_model.RelSegmentZone.zone_id == sql_model.Zone.id)\
            .join(sql_model.Segment, sql_model.RelSegmentZone.segment_id == sql_model.Segment.id)\
            .join(sql_model.Excursion, sql_model.Excursion.id == sql_model.Segment.excursion_id)\
            .join(sql_model.Vessel, sql_model.Excursion.vessel_id == sql_model.Vessel.id)\
            .where(
                and_(sql_model.Zone.id == zone_id,
                    or_(
                        sql_model.Segment.timestamp_start.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Segment.timestamp_end.between(datetime_range.start_at,datetime_range.end_at),))
                )\
            .group_by(sql_model.Zone.id,sql_model.Vessel.id)
            
            stmt =  stmt.order_by(func.sum(sql_model.Segment.segment_duration).asc())\
                    if  order.order == OrderByEnum.ascending \
                    else stmt.order_by(func.sum(sql_model.Segment.segment_duration).desc())
            stmt = stmt.offset(pagination.offset) if pagination.offset != None else stmt
            stmt = stmt.limit(pagination.limit) if pagination.limit != None else stmt

            payload=session.execute(stmt).all()
        return payload
    
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
                .where(
                and_(sql_model.Excursion.vessel_id == vessel_id,
                    or_(
                        sql_model.Excursion.departure_at.between(datetime_range.start_at,datetime_range.end_at),
                        sql_model.Excursion.arrival_at.between(datetime_range.start_at,datetime_range.end_at),))
                )\
                .group_by(sql_model.Excursion.vessel_id)\
                .union(select(
                    literal_column(vessel_id),
                    literal_column(f"'{activity_type.type.value}'"),
                    literal_column('0 seconds'),
                ))
            payload=session.execute(stmt.limit(1)).all()[0]
        return payload