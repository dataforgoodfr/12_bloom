from bloom.domain.rules import execute_rule_low_speed
from bloom.domain.vessel import Vessel
from bloom.infra.file_repository_polygons import PolygonFileRepository
from bloom.infra.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repository_vessel import VesselRepository


class ScrapVesselsAndGenerateAlertsFromMarineTraffic:
    def __init__(
        self,
        vessel_repository: VesselRepository,
        polygon_repository: PolygonFileRepository,
        scraper: MarineTrafficVesselScraper,
    ) -> None:
        self.vessel_repository = vessel_repository
        self.polygon_repository = polygon_repository
        self.scraper = scraper
        self.fishing_speed_limit = 2

    def generate_alerts_for_vessels_list(self) -> list[Vessel]:
        vessels_list = self.scrap_vessels()
        self.polygon_repository.load_polygons()
        alerts: list = []
        for vessel in vessels_list:
            if execute_rule_low_speed(
                vessel=vessel,
                polygon_list=self.polygon_repository.polygons,
            ):
                alerts.append(vessel)
        return alerts

    def scrap_vessels(self) -> list[Vessel]:
        vessels = self.vessel_repository.load_vessel_identifiers()

        scrapped_vessels = self.scraper.scrap_vessels(vessels)

        self.vessel_repository.save_vessels(scrapped_vessels)
        return scrapped_vessels
