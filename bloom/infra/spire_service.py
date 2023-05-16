import os

from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from requests import exceptions

from bloom.domain.vessel import Vessel
from bloom.infra.spire_api_paging import Paging
from bloom.logger import logger


class SpireService:
    def __init__(self) -> None:
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
        imo_list = [vessel["IMO"] for vessel in vessels]
        "\n".join(map(str, imo_list))

        return """
        query {
            vessels(
                imo: [
                    9175834
                    227302000
                    244309000
                    9204556
                    8028412
                    244070881
                    8707537
                    8209171
                    9074951
                    8716928
                    9126364
                    8707446
                    9182801
                    8301187
                    9690688
                    8918318
                    8707745
                    8224406
                    9828936
                    9187306
                    9249556
                    9249568
                    8901913
                ]
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

    def get_raw_vessels(self, vessels: list[Vessel]) -> list[str]:
        query_string = self.create_query_string(vessels)
        client = self.create_client()
        paging = Paging()
        hasnextpage: bool = False
        raw_vessels = []

        while True:
            try:
                response, hasnextpage = paging.page_and_get_response(
                    client,
                    query_string,
                )

                if response:
                    raw_vessels += response.get("vessels", {}).get("nodes", [])
                    if not hasnextpage:
                        break
            except BaseException:
                logger.exception("Error when paging")
                raise

        return raw_vessels

    def get_vessels(self, vessels: list[Vessel]) -> list[Vessel]:
        raw_vessels = self.get_raw_vessels(vessels)
        for raw_vessel in raw_vessels:
            vessels.append(self.format_raw_vessel(raw_vessel))

        return vessels

    def format_raw_vessel(self, raw_vessel: str) -> Vessel:
        return raw_vessel
