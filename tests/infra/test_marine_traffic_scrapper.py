from domain.vessel import Vessel
from infra.marine_traffic_scraper import MarineTrafficVesselScraper
from datetime import timezone


def test_scrapper_uses_local_time_in_same_timezone_as_scrapped_time():
    vessel_imo = 9175834
    test_vessel = Vessel(IMO=vessel_imo)
    marine_traffic_scrapper = MarineTrafficVesselScraper()

    scrapped_vessel = marine_traffic_scrapper.scrap_vessel(vessel=test_vessel)

    assert scrapped_vessel.last_position_time.tzinfo == scrapped_vessel.timestamp.tzinfo == timezone.utc

