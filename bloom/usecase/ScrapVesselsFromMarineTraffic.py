from bloom.infra.marine_traffic_scraper import Driver, MarineTrafficVesselScraper
from bloom.infra.repository_vessel import VesselRepository


class ScrapVesselsFromMarineTraffic:
    def __init__(
        self,
        vessel_repository: VesselRepository,
        scraper: MarineTrafficVesselScraper,
    ) -> None:
        self.vessel_repository = vessel_repository
        self.scraper = scraper

    def scrap_vessels(self) -> None:
        vessels = self.vessel_repository.load_vessel_identifiers()
        scrapped_vessels = []

        with Driver() as driver:
            for vessel in vessels:
                scrapped_vessels.append(self.scraper.scrap_vessel(driver, vessel))

        self.vessel_repository.save_vessels(scrapped_vessels)
