from datetime import datetime
from typing import Any

from pydantic import BaseModel
from functools import reduce

from typing import Union

class KplerAisData(BaseModel):
    id: Union[int, None] = None  # noqa: UP007
    position_id: Union[int, None] = None  # noqa: UP007
    vessel_uid: Union[int, None] = None  # noqa: UP007
    vessel_flag: Union[str, None] = None  # noqa: UP007
    vessel_name: Union[str, None] = None  # noqa: UP007
    vessel_callsign: Union[str, None] = None  # noqa: UP007
    vessel_mmsi: Union[int] = None  # noqa: UP007
    vessel_imo: Union[int, None] = None  # noqa: UP007
    vessel_marinetraffic_type: Union[str, None] = None  # noqa: UP007
    vessel_ais_type: Union[int, None] = None  # noqa: UP007
    vessel_width: Union[float, None] = None  # noqa: UP007
    vessel_length: Union[float, None] = None  # noqa: UP007
    vessel_grt: Union[float, None] = None  # noqa: UP007
    vessel_dwt: Union[float, None] = None  # noqa: UP007
    static_timestamp: Union[datetime, None] = None  # noqa: UP007
    static_source: Union[str, None] = None  # noqa: UP007
    static_message_type: Union[int, None] = None  # noqa: UP007
    position_message_type: Union[int, None] = None  # noqa: UP007
    position_source: Union[str, None] = None  # noqa: UP007
    position_course: Union[float, None] = None  # noqa: UP007
    position_heading: Union[float, None] = None  # noqa: UP007
    position_longitude: Union[float, None] = None  # noqa: UP007
    position_latitude: Union[float, None] = None  # noqa: UP007
    position_navigational_status: Union[int, None] = None  # noqa: UP007
    position_rot: Union[float, None] = None  # noqa: UP007
    position_speed: Union[float, None] = None  # noqa: UP007
    position_timestamp: Union[datetime, None] = None  # noqa: UP007
    position_kpler_insert_timestamp: Union[datetime, None] = None  # noqa: UP007
    voyage_destination: Union[str, None] = None  # noqa: UP007
    voyage_draught: Union[float, None] = None  # noqa: UP007
    voyage_eta: Union[datetime, None] = None  # noqa: UP007
    payload: Union[dict, None] = None
    created_at: Union[datetime, None] = None  # noqa: UP007

    def map_from_kpler(message: dict[str, Any]):  # noqa: ANN201
        def deep_get(dictionary: dict[str, Any], *keys) -> str:
            return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)
        
        return KplerAisData(
            position_id=message["id"] if "id" in message.keys() else None,
            vessel_uid=deep_get(message, "properties", "vesselUid") if "properties" in message.keys() and "vesselUid" in message["properties"].keys() else None,
            vessel_flag=deep_get(message, "properties", "flag") if "properties" in message.keys() and "flag" in message["properties"].keys() else None,
            vessel_name=deep_get(message, "properties", "vesselName") if "properties" in message.keys() and "vesselName" in message["properties"].keys() else None,
            vessel_callsign=deep_get(message, "properties", "callsign") if "properties" in message.keys() and "callsign" in message["properties"].keys() else None,
            vessel_mmsi=deep_get(message, "properties", "mmsi") if "properties" in message.keys() and "mmsi" in message["properties"].keys() else None,
            vessel_imo=deep_get(message, "properties", "imo") if "properties" in message.keys() and "imo" in message["properties"].keys() else None,
            vessel_marinetraffic_type=deep_get(message, "properties", "vesselType") if "properties" in message.keys() and "vesselType" in message["properties"].keys() else None,
            vessel_ais_type=deep_get(message, "properties", "vesselTypeAis") if "properties" in message.keys() and "vesselTypeAis" in message["properties"].keys() else None,
            vessel_width=deep_get(message, "properties", "width") if "properties" in message.keys() and "width" in message["properties"].keys() else None,
            vessel_length=deep_get(message, "properties", "length") if "properties" in message.keys() and "length" in message["properties"].keys() else None,
            vessel_grt=deep_get(message, "properties", "grt") if "properties" in message.keys() and "grt" in message["properties"].keys() else None,
            vessel_dwt=deep_get(message, "properties", "dwt") if "properties" in message.keys() and "dwt" in message["properties"].keys() else None,
            static_timestamp=deep_get(message, "properties", "staticDt") if "properties" in message.keys() and "staticDt" in message["properties"].keys() else None,
            static_source=deep_get(message, "properties", "staticSrc") if "properties" in message.keys() and "staticSrc" in message["properties"].keys() else None,
            static_message_type=deep_get(message, "properties", "staticMsgType") if "properties" in message.keys() and "staticMsgType" in message["properties"].keys() else None,
            position_message_type=deep_get(message, "properties", "posMsgType") if "properties" in message.keys() and "posMsgType" in message["properties"].keys() else None,
            position_source=deep_get(message, "properties", "posSrc") if "properties" in message.keys() and "posSrc" in message["properties"].keys() else None,
            position_course=deep_get(message, "properties", "cog") if "properties" in message.keys() and "cog" in message["properties"].keys() else None,
            position_heading=deep_get(message, "properties", "heading") if "properties" in message.keys() and "heading" in message["properties"].keys() else None,
            position_longitude=deep_get(message, "properties", "longitude") if "properties" in message.keys() and "longitude" in message["properties"].keys() else None,
            position_latitude=deep_get(message, "properties", "latitude") if "properties" in message.keys() and "latitude" in message["properties"].keys() else None,
            position_navigational_status=deep_get(message, "properties", "navStatus") if "properties" in message.keys() and "navStatus" in message["properties"].keys() else None,
            position_rot=deep_get(message, "properties", "rot") if "properties" in message.keys() and "rot" in message["properties"].keys() else None,
            position_speed=deep_get(message, "properties", "sog") if "properties" in message.keys() and "sog" in message["properties"].keys() else None,
            position_timestamp=deep_get(message, "properties", "posDt") if "properties" in message.keys() and "posDt" in message["properties"].keys() else None,
            position_kpler_insert_timestamp=deep_get(message, "properties", "insertDt") if "properties" in message.keys() and "insertDt" in message["properties"].keys() else None,
            voyage_destination=deep_get(message, "properties", "destination") if "properties" in message.keys() and "destination" in message["properties"].keys() else None,
            voyage_draught=deep_get(message, "properties", "draught") if "properties" in message.keys() and "draught" in message["properties"].keys() else None,
            voyage_eta=deep_get(message, "properties", "eta") if "properties" in message.keys() and "eta" in message["properties"].keys() else None,
            payload=message
        )