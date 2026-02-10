from typing import Any

from bloom.config import settings
from bloom.domain.vessel import Vessel
from bloom.infra.http.spire_api_utils import Paging
from bloom.logger import logger
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from requests import exceptions


class GetVesselsFromSpire:
    def __init__(self) -> None:
        spire_token = settings.spire_token

        self.transport = RequestsHTTPTransport(
            url="https://api.sml.kpler.com/graphql",
            headers={"Authorization": "Bearer " + spire_token},
            verify=True,
            retries=3,
            timeout=30,
        )

    def create_client(self) -> Client:
        try:
            client = Client(transport=self.transport, fetch_schema_from_transport=True)
        except exceptions.ConnectTimeout:
            logger.exception("Connection failed")
            raise
        return client

    def create_query_string(self, vessels: list[Vessel]) -> str:
        mmsi_list = [vessel.mmsi for vessel in vessels]

        return (
            """
        query {
            vessels(
                mmsi: [ """
            + "\n".join(map(str, mmsi_list))  # get_should send a str ?
            + """ ]
            ) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    updateTimestamp
                    staticData {
                        aisClass
                        flag
                        name
                        callsign
                        timestamp
                        updateTimestamp
                        shipType
                        shipSubType
                        mmsi
                        imo
                        dimensions {
                            width
                            length
                        }
                    }
                    lastPositionUpdate {
                        accuracy
                        collectionType
                        course
                        heading
                        latitude
                        longitude
                        maneuver
                        navigationalStatus
                        rot
                        speed
                        timestamp
                        updateTimestamp
                    }
                    currentVoyage {
                        destination
                        draught
                        eta
                        timestamp
                        updateTimestamp
                    }
                }
            }
        }
        """
        )

    def get_raw_vessels_from_spire(self, vessels: list[Vessel]) -> list[dict[str, Any]]:
        query_string = self.create_query_string(vessels)
        client = self.create_client()
        paging = Paging()

        raw_vessels = paging.page_and_get_response(
            client,
            query_string,
        )
        return raw_vessels
