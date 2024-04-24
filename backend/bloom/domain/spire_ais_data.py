from datetime import datetime
from typing import Any  # FIXME: Self only supported by python3.11 and onwards

from pydantic import BaseModel
from functools import reduce

from typing import Union


class SpireAisData(BaseModel):
    id: Union[int, None] = None  # noqa: UP007
    spire_update_statement: datetime
    vessel_ais_class: Union[str, None] = None  # noqa: UP007
    vessel_flag: Union[str, None] = None  # noqa: UP007
    vessel_name: Union[str, None] = None  # noqa: UP007
    vessel_callsign: Union[str, None] = None  # noqa: UP007
    vessel_timestamp: Union[datetime, None] = None  # noqa: UP007
    vessel_update_timestamp: Union[datetime, None] = None  # noqa: UP007
    vessel_ship_type: Union[str, None] = None  # noqa: UP007
    vessel_sub_ship_type: Union[str, None] = None  # noqa: UP007
    vessel_mmsi: Union[int, None] = None  # noqa: UP007
    vessel_imo: Union[int, None] = None  # noqa: UP007
    vessel_width: Union[int, None] = None  # noqa: UP007
    vessel_length: Union[int, None] = None  # noqa: UP007
    position_accuracy: Union[str, None] = None  # noqa: UP007
    position_collection_type: Union[str, None] = None  # noqa: UP007
    position_course: Union[float, None] = None  # noqa: UP007
    position_heading: Union[float, None] = None  # noqa: UP007
    position_latitude: Union[float, None] = None  # noqa: UP007
    position_longitude: Union[float, None] = None  # noqa: UP007
    position_maneuver: Union[str, None] = None  # noqa: UP007
    position_navigational_status: Union[str, None] = None  # noqa: UP007
    position_rot: Union[float, None] = None  # noqa: UP007
    position_speed: Union[float, None] = None  # noqa: UP007
    position_timestamp: Union[datetime, None] = None  # noqa: UP007
    position_update_timestamp: Union[datetime, None] = None  # noqa: UP007
    voyage_destination: Union[str, None] = None  # noqa: UP007
    voyage_draught: Union[float, None] = None  # noqa: UP007
    voyage_eta: Union[datetime, None] = None  # noqa: UP007
    voyage_timestamp: Union[datetime, None] = None  # noqa: UP007
    voyage_update_timestamp: Union[datetime, None] = None  # noqa: UP007
    created_at: Union[datetime, None] = None  # noqa: UP007

    def map_from_spire(spire_update_timestamp: datetime, vessel: dict[str, Any]):  # noqa: ANN201
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
