from typing import Any
from bloom.domain.kpler_ais_data import KplerAisData
from gql import Client, gql

from bloom.logger import logger

def map_raw_messages_to_domain(raw_messages: list[dict[str, Any]]) -> list[KplerAisData]:
    kpler_ais_data = []
    for vessel in raw_messages:
        kpler_ais_data.append(KplerAisData.map_from_kpler(vessel))
    return kpler_ais_data