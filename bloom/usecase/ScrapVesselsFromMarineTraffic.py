from bloom.domain.vessel import Vessel, VesselPositionMarineTraffic
from bloom.infra.http.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repositories.repository_vessel import RepositoryVessel
from bloom.logger import logger


class ScrapVesselsFromMarineTraffic:
    def __init__(
        self,
        vessel_repository: RepositoryVessel,
        scraper: MarineTrafficVesselScraper,
    ) -> None:
        self.vessel_repository: RepositoryVessel = vessel_repository
        self.scraper: MarineTrafficVesselScraper = scraper

    def scrap_vessels(self) -> None:
        vessels: list[Vessel] = self.vessel_repository.load_vessel_identifiers()

        for chunk in self.batch(vessels, 10):
            logger.info(
                "Start to scrap chunk",
            )
            scrapped_vessels: list[
                VesselPositionMarineTraffic
            ] = self.scraper.scrap_vessels(chunk)

            logger.info(
                "Start to save chunk",
            )
            self.vessel_repository.save_marine_traffic_vessels_positions(
                scrapped_vessels,
            )

    def batch(self, iterable, n=1):  # noqa: ANN201 ANN001
        length = len(iterable)
        for ndx in range(0, length, n):
            yield iterable[ndx : min(ndx + n, length)]
