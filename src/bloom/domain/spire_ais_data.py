from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel
from functools import reduce

from typing import Union


class SpireAisData(BaseModel):
    id: int | None = None
    spire_update_statement: datetime
    vessel_ais_class: str | None
    vessel_flag: str | None
    vessel_name: str | None
    vessel_callsign: str | None
    vessel_timestamp: datetime
    vessel_update_timestamp: datetime
    vessel_ship_type: str | None
    vessel_sub_ship_type: str | None
    vessel_mmsi: int | None
    vessel_imo: int | None
    vessel_width: int | None
    vessel_length: int | None
    position_accuracy: str | None
    position_collection_type: str | None
    position_course: float | None
    position_heading: float | None
    position_latitude: float | None
    position_longitude: float | None
    position_maneuver: str | None
    position_navigational_status: str | None
    position_rot: float | None
    position_speed: float | None
    position_timestamp: datetime
    position_update_timestamp: datetime
    voyage_destination: str | None
    voyage_draught: float | None
    voyage_eta: datetime | None
    voyage_timestamp: datetime
    voyage_update_timestamp: datetime
    created_at: Union[datetime, None] = None

    def map_from_spire(spire_update_timestamp: datetime, vessel: dict[str, Any]) -> Self:
        def deep_get(dictionary: dict[str, Any], *keys) -> str:
            return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

        return SpireAisData(
            spire_update_statement=spire_update_timestamp,
            vessel_ais_class=deep_get(vessel, "staticData", "aisClass"),
            vessel_flag=deep_get(vessel, "staticData", "flag"),
            vessel_name=deep_get(vessel, "staticData", "name"),
            vessel_callsign=deep_get(vessel, "staticData", "callsign"),
            vessel_timestamp=deep_get(vessel, "staticData", "timestamp"),
            vessel_update_timestamp=deep_get(vessel, "staticData", "updateTimestamp"),
            vessel_ship_type=deep_get(vessel, "staticData", "shipType"),
            vessel_sub_ship_type=deep_get(vessel, "staticData", "shipSubType"),
            vessel_mmsi=deep_get(vessel, "staticData", "mmsi"),
            vessel_imo=deep_get(vessel, "staticData", "imo"),
            vessel_width=deep_get(vessel, "staticData", "dimensions", "width"),
            vessel_length=deep_get(vessel, "staticData", "dimensions", "length"),
            position_accuracy=deep_get(vessel, "lastPositionUpdate", "accuracy"),
            position_collection_type=deep_get(vessel, "lastPositionUpdate", "collectionType"),
            position_course=deep_get(vessel, "lastPositionUpdate", "course"),
            position_heading=deep_get(vessel, "lastPositionUpdate", "heading"),
            position_latitude=deep_get(vessel, "lastPositionUpdate", "latitude"),
            position_longitude=deep_get(vessel, "lastPositionUpdate", "longitude"),
            position_maneuver=deep_get(vessel, "lastPositionUpdate", "maneuver"),
            position_navigational_status=deep_get(
                vessel, "lastPositionUpdate", "navigationalStatus"
            ),
            position_rot=deep_get(vessel, "lastPositionUpdate", "rot"),
            position_speed=deep_get(vessel, "lastPositionUpdate", "speed"),
            position_timestamp=deep_get(vessel, "lastPositionUpdate", "timestamp"),
            position_update_timestamp=deep_get(vessel, "lastPositionUpdate", "updateTimestamp"),
            voyage_destination=deep_get(vessel, "currentVoyage", "destination"),
            voyage_draught=deep_get(vessel, "currentVoyage", "draught"),
            voyage_eta=deep_get(vessel, "currentVoyage", "eta"),
            voyage_timestamp=deep_get(vessel, "currentVoyage", "timestamp"),
            voyage_update_timestamp=deep_get(vessel, "currentVoyage", "updateTimestamp"),
        )
