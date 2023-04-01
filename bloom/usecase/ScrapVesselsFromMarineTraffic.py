from bloom.domain.vessel import Vessel, VesselPositionMarineTraffic
from bloom.infra.http.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repositories.sql_repository_vessel import SqlRepositoryVessel


class ScrapVesselsFromMarineTraffic:
    def __init__(
        self,
        vessel_repository: SqlRepositoryVessel,
        scraper: MarineTrafficVesselScraper,
    ) -> None:
        self.vessel_repository: SqlRepositoryVessel = vessel_repository
        self.scraper: MarineTrafficVesselScraper = scraper

    def scrap_vessels(self) -> None:
        vessels: list[Vessel] = self.vessel_repository.load_vessel_identifiers()

        scrapped_vessels: list[
            VesselPositionMarineTraffic
        ] = self.scraper.scrap_vessels(vessels)

        self.vessel_repository.save_vessels_positions(scrapped_vessels)
