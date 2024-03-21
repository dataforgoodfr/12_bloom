import uuid
from typing import Any

import folium
from bloom.config import settings
from bloom.infra.database.database_manager import Base
from geoalchemy2 import Geometry
from shapely import wkb
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Double,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.sql import func


class Vessel(Base):
    __tablename__ = "dim_vessel"
    id = Column("id", Integer, primary_key=True)
    mmsi = Column("mmsi", Integer, unique=True)
    ship_name = Column("ship_name", String, nullable=False)
    width = Column("width", Double)
    length = Column("length", Double)
    country_iso3 = Column("country_iso3", String, nullable=False)
    type = Column("type", String)
    imo = Column("imo", Integer)
    cfr = Column("cfr", String)
    registration_number = Column("registration_number", String)
    external_marking = Column("external_marking", String)
    ircs = Column("ircs", String)
    mt_activated = Column("mt_activated", Boolean, nullable=False)
    home_port_id = Column("home_port_id", Integer, ForeignKey("dim_port.id"))
    created_at = Column(
        "created_at", DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column("updated_at", DateTime(timezone=True), onupdate=func.now())


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
    position = Column("position", Geometry("POINT"))
    speed = Column("speed", Float)
    navigation_status = Column("navigation_status", String)
    vessel_length = Column("vessel_length", Integer)
    vessel_width = Column("vessel_width", Integer)
    voyage_destination = Column("voyage_destination", String)
    voyage_draught = Column("voyage_draught", Float)
    voyage_eta = Column("voyage_eta", DateTime)
    accuracy = Column("accuracy", String)
    position_sensors = Column("position_sensors", String)
    course = Column("course", Float)
    heading = Column("heading", Float)
    rot = Column("rot", Float)


class Alert(Base):
    __tablename__ = "alert"
    id = Column("id", Integer, primary_key=True, index=True)
    timestamp = Column("timestamp", DateTime)
    mpa_id = Column("mpa_id", Integer)
    vessel_id = Column("vessel_id", Integer)


IUCN_CATEGORIES = {
    "Ia": {"name": "Strict Nature Reserve", "color": "#FF0000"},  # Red
    "Ib": {"name": "Wilderness Area", "color": "#FF3300"},  #
    "II": {"name": "National Park", "color": "#FF6600"},  #
    "III": {"name": "Natural Monument or Feature", "color": "#FF9900"},  #
    "IV": {"name": "Habitat/Species Management Area", "color": "#FFCC00"},  #
    "V": {"name": "Protected Landscape/Seascape", "color": "#FFFF00"},  #
    "VI": {
        "name": "Protected area with sustainable use of natural resources",
        "color": "#FFFF66",
    },  # Yellow
}


class MPA(Base):
    __tablename__ = "mpa_fr_with_mn"
    geometry = Column("geometry", Geometry("POLYGON"))
    # gov_type = Column("GOV_TYPE", Text)
    iucn_category = Column("IUCN_CAT", Text)
    name = Column("name", Text, nullable=False)
    type = Column("DESIG_TYPE", Text)
    index = Column("index", Integer, primary_key=True)
    wdpaid = Column("WDPAID", Float)
    eng = Column("DESIG_ENG", Text)
    parent_iso = Column("PARENT_ISO", Text)
    iso3 = Column("ISO3", Text)
    benificiaries = Column("Benificiaries", Text)

    def __repr__(self) -> str:
        return (
            f"MarineProtectedArea(name={self.name},"
            f"type={self.type},iucn_category={self.iucn_category})"
        )

    def get_polygon(self) -> Any:
        shapely_polygon = wkb.loads(bytes(self.geometry.data))
        return shapely_polygon.__geo_interface__

    @property
    def protected_area_category(self) -> str:
        return IUCN_CATEGORIES.get(self.iucn_category, {"name": "Unknown"})["name"]

    @property
    def color(self) -> str:
        return IUCN_CATEGORIES.get(self.iucn_category, {"color": "#808080"})["color"]

    def add_to_map(self, m: folium.Map, show_iucn: bool = True) -> None:
        polygon = self.get_polygon()
        color = self.color

        if show_iucn:
            folium.GeoJson(
                polygon,
                style_function=lambda _, color=color: {
                    "fillColor": color,
                    "color": color,
                },
                tooltip=f"Protected area : {self.name}, "
                f"IUCN category :{self.iucn_category} "
                f"{self.protected_area_category}",
            ).add_to(m)

        else:
            folium.GeoJson(polygon).add_to(m)


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
