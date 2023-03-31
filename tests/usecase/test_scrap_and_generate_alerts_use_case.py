from unittest import mock

from shapely import Point

from bloom.domain.vessel import VesselPositionMarineTraffic
from bloom.infra.repositories.file_repository_polygons import PolygonFileRepository
from bloom.infra.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repositories.repository_vessel import RepositoryVessel
from bloom.usecase.ScrapVesselsAndGenerateAlertsFromMarineTraffic import (
    ScrapVesselsAndGenerateAlertsFromMarineTraffic,
)

test_vessel = VesselPositionMarineTraffic(
    vessel_id="32",
    timestamp="2023-03-12 12:31 UTC",
    ship_name="ZEELAND",
    IMO="8901913",
    last_position_time="2023-03-12 12:30 UTC",
    position=Point(-61.85589548359167, 17.195012165330123),
    status="ACTIVE",
    speed=0.0,
    navigation_status="Moored",
)


def test_generate_alerts_for_vessels_list_adds_single_alert_for_vessel():
    vessel_repository = mock.Mock(spec=RepositoryVessel)
    vessel_repository.load_vessel_identifiers.return_value = ["8901913"]
    vessel_scrapper = mock.Mock(spec=MarineTrafficVesselScraper)
    vessel_scrapper.scrap_vessels.return_value = [test_vessel]
    polygon_repository = PolygonFileRepository()

    expected_alerts = [test_vessel]

    alerts_generator_use_case = ScrapVesselsAndGenerateAlertsFromMarineTraffic(
        vessel_repository=vessel_repository,
        polygon_repository=polygon_repository,
        scraper=vessel_scrapper,
    )
    actual_alerts = alerts_generator_use_case.generate_alerts_for_vessels_list()

    assert actual_alerts == expected_alerts
