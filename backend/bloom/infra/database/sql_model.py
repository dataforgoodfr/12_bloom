from bloom.config import settings
from bloom.infra.database.database_manager import Base
from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Double,
    ForeignKey,
    Integer,
    Interval,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class Vessel(Base):
    __tablename__ = "dim_vessel"
    id = Column("id", Integer, primary_key=True)
    mmsi = Column("mmsi", Integer)
    ship_name = Column("ship_name", String, nullable=False)
    width = Column("width", Double)
    length = Column("length", Double)
    country_iso3 = Column("country_iso3", String, nullable=False)
    type = Column("type", String)
    imo = Column("imo", Integer)
    cfr = Column("cfr", String)
    external_marking = Column("external_marking", String)
    ircs = Column("ircs", String)
    tracking_activated = Column("tracking_activated", Boolean, nullable=False)
    tracking_status = Column("tracking_status", String)
    home_port_id = Column("home_port_id", Integer, ForeignKey("dim_port.id"))
    details = Column("details", String)
    check = Column("check", String)
    length_class = Column("length_class", String)
    created_at = Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


class Alert(Base):
    __tablename__ = "alert"
    id = Column("id", Integer, primary_key=True, index=True)
    timestamp = Column("timestamp", DateTime)
    mpa_id = Column("mpa_id", Integer)
    vessel_id = Column("vessel_id", Integer)


class Port(Base):
    __tablename__ = "dim_port"
    id = Column("id", Integer, primary_key=True, index=True)
    name = Column("name", String, nullable=False)
    locode = Column("locode", String, nullable=False)
    url = Column("url", String)
    country_iso3 = Column("country_iso3", String)
    latitude = Column("latitude", Double)
    longitude = Column("longitude", Double)
    geometry_point = Column("geometry_point", Geometry("POINT", srid=settings.srid))
    geometry_buffer = Column("geometry_buffer", Geometry("POLYGON", srid=settings.srid))
    has_excursion = Column("has_excursion", Boolean, default=False)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


class SpireAisData(Base):
    __tablename__ = "spire_ais_data"

    id = Column("id", Integer, primary_key=True)
    spire_update_statement = Column("spire_update_statement", DateTime(timezone=True))
    vessel_ais_class = Column("vessel_ais_class", String)
    vessel_flag = Column("vessel_flag", String)
    vessel_name = Column("vessel_name", String)
    vessel_callsign = Column("vessel_callsign", String)
    vessel_timestamp = Column("vessel_timestamp", DateTime(timezone=True))
    vessel_update_timestamp = Column("vessel_update_timestamp", DateTime(timezone=True))
    vessel_ship_type = Column("vessel_ship_type", String)
    vessel_sub_ship_type = Column("vessel_sub_ship_type", String)
    vessel_mmsi = Column("vessel_mmsi", Integer)
    vessel_imo = Column("vessel_imo", Integer)
    vessel_width = Column("vessel_width", Integer)
    vessel_length = Column("vessel_length", Integer)
    position_accuracy = Column("position_accuracy", String)
    position_collection_type = Column("position_collection_type", String)
    position_course = Column("position_course", Double)
    position_heading = Column("position_heading", Double)
    position_latitude = Column("position_latitude", Double)
    position_longitude = Column("position_longitude", Double)
    position_maneuver = Column("position_maneuver", String)
    position_navigational_status = Column("position_navigational_status", String)
    position_rot = Column("position_rot", Double)
    position_speed = Column("position_speed", Double)
    position_timestamp = Column("position_timestamp", DateTime(timezone=True))
    position_update_timestamp = Column("position_update_timestamp", DateTime(timezone=True))
    voyage_destination = Column("voyage_destination", String)
    voyage_draught = Column("voyage_draught", Double)
    voyage_eta = Column("voyage_eta", DateTime(timezone=True))
    voyage_timestamp = Column("voyage_timestamp", DateTime(timezone=True))
    voyage_update_timestamp = Column("voyage_update_timestamp", DateTime(timezone=True))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())


class Zone(Base):
    __tablename__ = "dim_zone"
    id = Column("id", Integer, primary_key=True)
    category = Column("category", String, nullable=False)
    sub_category = Column("sub_category", String)
    name = Column("name", String, nullable=False)
    geometry = Column("geometry", Geometry(geometry_type="GEOMETRY", srid=settings.srid))
    centroid = Column("centroid", Geometry(geometry_type="POINT", srid=settings.srid))
    json_data = Column("json_data", JSONB)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())


class WhiteZone(Base):
    __tablename__ = "dim_white_zone"
    id = Column("id", Integer, primary_key=True)
    geometry = Column("geometry", Geometry(geometry_type="GEOMETRY", srid=settings.srid))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


class VesselPosition(Base):
    __tablename__ = "vessel_positions"
    id = Column("id", Integer, primary_key=True)
    timestamp = Column("timestamp", DateTime(timezone=True), nullable=False)
    accuracy = Column("accuracy", String)
    collection_type = Column("collection_type", String)
    course = Column("course", Double)
    heading = Column("heading", Double)
    position = Column("position", Geometry(geometry_type="POINT", srid=settings.srid), nullable=False)
    latitude = Column("latitude", Double)
    longitude = Column("longitude", Double)
    maneuver = Column("maneuver", String)
    navigational_status = Column("navigational_status", String)
    rot = Column("rot", Double)
    speed = Column("speed", Double)
    vessel_id = Column("vessel_id", Integer, ForeignKey("dim_vessel.id"), nullable=False)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())


class VesselData(Base):
    __tablename__ = "vessel_data"
    id = Column("id", Integer, primary_key=True)
    timestamp = Column("timestamp", DateTime(timezone=True), nullable=False)
    ais_class = Column("ais_class", String)
    flag = Column("flag", String)
    name = Column("name", String)
    callsign = Column("callsign", String)
    ship_type = Column("ship_type", String)
    sub_ship_type = Column("sub_ship_type", String)
    mmsi = Column("mmsi", Integer)
    imo = Column("imo", Integer)
    width = Column("width", Integer)
    length = Column("length", Integer)
    vessel_id = Column("vessel_id", Integer, ForeignKey("dim_vessel.id"), nullable=False)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())


class VesselVoyage(Base):
    __tablename__ = "vessel_voyage"
    id = Column("id", Integer, primary_key=True)
    timestamp = Column("timestamp", DateTime(timezone=True), nullable=False)
    destination = Column("destination", String)
    draught = Column("draught", Double)
    eta = Column("eta", DateTime(timezone=True))
    vessel_id = Column("vessel_id", Integer, ForeignKey("dim_vessel.id"), nullable=False)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())


class Excursion(Base):
    __tablename__ = "fct_excursion"
    id = Column("id", Integer, primary_key=True)
    vessel_id = Column("vessel_id", Integer, ForeignKey("dim_vessel.id"), nullable=False)
    departure_port_id = Column("departure_port_id", Integer, ForeignKey("dim_port.id"))
    departure_at = Column("departure_at", DateTime(timezone=True))
    departure_position = Column("departure_position", Geometry(geometry_type="POINT", srid=settings.srid))
    arrival_port_id = Column("arrival_port_id", Integer, ForeignKey("dim_port.id"))
    arrival_at = Column("arrival_at", DateTime(timezone=True))
    arrival_position = Column("arrival_position", Geometry(geometry_type="POINT", srid=settings.srid))
    excursion_duration = Column("excursion_duration", Interval)
    total_time_at_sea = Column("total_time_at_sea", Interval)
    total_time_in_amp = Column("total_time_in_amp", Interval)
    total_time_in_territorial_waters = Column("total_time_in_territorial_waters", Interval)
    total_time_in_costal_waters = Column("total_time_in_costal_waters", Interval)
    total_time_fishing = Column("total_time_fishing", Interval)
    total_time_fishing_in_amp = Column("total_time_fishing_in_amp", Interval)
    total_time_fishing_in_territorial_waters = Column("total_time_fishing_in_territorial_waters", Interval)
    total_time_fishing_in_costal_waters = Column("total_time_fishing_in_costal_waters", Interval)
    total_time_extincting_amp = Column("total_time_extincting_amp", Interval)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


class Segment(Base):
    __tablename__ = "fct_segment"
    id = Column("id", Integer, primary_key=True)
    excursion_id = Column("excursion_id", Integer, ForeignKey("fct_excursion.id"), nullable=False)
    timestamp_start = Column("timestamp_start", DateTime(timezone=True))
    timestamp_end = Column("timestamp_end", DateTime(timezone=True))
    segment_duration = Column("segment_duration", Interval)
    start_position = Column("start_position", Geometry(geometry_type="POINT", srid=settings.srid))
    end_position = Column("end_position", Geometry(geometry_type="POINT", srid=settings.srid))
    heading = Column("heading", Double)
    distance = Column("distance", Double)
    average_speed = Column("average_speed", Double)
    speed_at_start = Column("speed_at_start", Double)
    speed_at_end = Column("speed_at_end", Double)
    heading_at_start = Column("heading_at_start", Double)
    heading_at_end = Column("heading_at_end", Double)
    type = Column("type", String)
    in_amp_zone = Column("in_amp_zone", Boolean)
    in_territorial_waters = Column("in_territorial_waters", Boolean)
    in_costal_waters = Column("in_costal_waters", Boolean)
    last_vessel_segment = Column("last_vessel_segment", Boolean)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


class TaskExecution(Base):
    __tablename__ = "tasks_executions"
    task_name = Column("task_name", String, primary_key=True)
    point_in_time = Column("point_in_time", DateTime(timezone=True))
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())
