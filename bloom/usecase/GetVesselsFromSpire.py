import os

from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from requests import exceptions

from bloom.domain.vessel import Vessel
from bloom.infra.database import sql_model
from bloom.infra.http.spire_api_utils import Paging
from bloom.infra.repositories.repository_vessel import RepositoryVessel
from bloom.logger import logger


class GetVesselsFromSpire:
    def __init__(
        self,
        vessel_repository: RepositoryVessel,
    ) -> None:

        self.vessel_repository: RepositoryVessel = vessel_repository

        spire_token = os.environ.get("SPIRE_TOKEN")

        self.transport = RequestsHTTPTransport(
            url="https://api.spire.com/graphql",
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
        imo_list = [vessel.get_imo() for vessel in vessels]

        return (
            """
        query {
            vessels(
                imo: [ """
            + "\n".join(map(str, imo_list))  # get_should send a str ?
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
                        callsign
                        dimensions {
                            a
                            b
                            c
                            d
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

    def get_raw_vessels(self, vessels: list[Vessel]) -> list[str]:
        query_string = self.create_query_string(vessels)
        client = self.create_client()
        paging = Paging()

        return paging.page_and_get_response(
            client,
            query_string,
        )

    def get_all_vessels(self) -> list[sql_model.VesselPositionSpire]:
        vessels: list[Vessel] = self.vessel_repository.load_vessel_identifiers()
        raw_vessels = self.get_raw_vessels(vessels)

        map_id = {}
        for vessel in vessels:
            map_id[int(vessel.get_imo())] = vessel.vessel_id

        return [
            RepositoryVessel.map_json_vessel_to_sql_spire(
                vessel,
                map_id.get(vessel["staticData"]["imo"]),
            )
            for vessel in raw_vessels
        ]

    def save_vessels(self, vessels: list[sql_model.VesselPositionSpire]) -> None:
        self.vessel_repository.save_spire_vessels_positions(vessels)
