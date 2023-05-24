from bloom.domain.rules import execute_rule_low_speed
from bloom.domain.vessel import Vessel, VesselPositionMarineTraffic
from bloom.infra.http.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repositories.file_repository_polygons import PolygonFileRepository
from bloom.infra.repositories.repository_vessel import RepositoryVessel


class ScrapVesselsAndGenerateAlertsFromMarineTraffic:
    def __init__(
        self,
        vessel_repository: RepositoryVessel,
        polygon_repository: PolygonFileRepository,
        scraper: MarineTrafficVesselScraper,
    ) -> None:
        self.vessel_repository: RepositoryVessel = vessel_repository
        self.polygon_repository: PolygonFileRepository = polygon_repository
        self.scraper: MarineTrafficVesselScraper = scraper
        self.fishing_speed_limit: float = 2

    def generate_alerts_for_vessels_list(self) -> list[VesselPositionMarineTraffic]:
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

    def scrap_vessels(self) -> list[VesselPositionMarineTraffic]:
        vessels: list[Vessel] = self.vessel_repository.load_vessel_metadata()

        scrapped_vessels: list[
            VesselPositionMarineTraffic
        ] = self.scraper.scrap_vessels(vessels)

        self.vessel_repository.save_marine_traffic_vessels_positions(scrapped_vessels)
        return scrapped_vessels
