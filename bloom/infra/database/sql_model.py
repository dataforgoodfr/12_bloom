import uuid

from geoalchemy2 import Geometry
from sqlalchemy import UUID, Boolean, Column, DateTime, Float, Integer, String

from bloom.infra.database.database_manager import Base


class Vessel(Base):
    __tablename__ = "vessels"
    id = Column("id", Integer, primary_key=True, index=True)
    country_iso3 = Column(String)
    cfr = Column(String)
    IMO = Column(String, index=True, nullable=False)
    registration_number = Column(String)
    external_marking = Column(String)
    ship_name = Column(String)
    ircs = Column(String)
    mmsi = Column(String)
    loa = Column(Float)
    type = Column(String)
    mt_activated = Column(Boolean)


class VesselPositionMarineTraffic(Base):
    __tablename__ = "marine_traffic_vessel_positions"
    id = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    timestamp = Column("timestamp", DateTime)
    ship_name = Column("ship_name", String)
    IMO = Column("IMO", String, index=True, nullable=False)
    vessel_id = Column("vessel_id", Integer, index=True)
    mmsi = Column("mmsi", String)
    last_position_time = Column("last_position_time", DateTime)
    fishing = Column("fishing", Boolean)
    at_port = Column("at_port", Boolean)
    port_name = Column("port_name", String)
    position = Column("position", Geometry("POINT"))
    status = Column("status", String)
    speed = Column("speed", Float)
    navigation_status = Column("navigation_status", String)


class VesselPositionSpire(Base):
    __tablename__ = "spire_vessel_positions"
    id = Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    timestamp = Column("timestamp", DateTime)
    ship_name = Column("ship_name", String)
    IMO = Column("IMO", String, index=True, nullable=False)
    vessel_id = Column("vessel_id", Integer, index=True)
    mmsi = Column("mmsi", String)
    last_position_time = Column("last_position_time", DateTime)
    fishing = Column("fishing", Boolean)
    at_port = Column("at_port", Boolean)
    port_name = Column("port_name", String)
    position = Column("position", Geometry("POINT"))
    status = Column("status", String)
    speed = Column("speed", Float)
    navigation_status = Column("navigation_status", String)


class Alert(Base):
    __tablename__ = "alert"
    id = Column("id", Integer, primary_key=True, index=True)
    id_mpa = Column("id", Integer)
    id_boat = Column("id", UUID(as_uuid=True))
    timestamp = Column("timestamp", DateTime)
    mmsi = Column("mmsi", String)
