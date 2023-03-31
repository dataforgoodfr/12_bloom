# ruff: noqa: ANN201
from datetime import timezone
from subprocess import PIPE, Popen

from bloom.domain.vessel import VesselPositionMarineTraffic
from bloom.infra.marine_traffic_scraper import Driver, MarineTrafficVesselScraper


def test_scrapper_uses_local_time_in_same_timezone_as_scrapped_time():
    vessel_imo = 9175834
    test_vessels = [VesselPositionMarineTraffic(IMO=vessel_imo)]
    marine_traffic_scrapper = MarineTrafficVesselScraper()

    scrapped_vessel = marine_traffic_scrapper.scrap_vessels(
        vessels=test_vessels,
    )[0]

    assert (
        scrapped_vessel.last_position_time.tzinfo
        == scrapped_vessel.timestamp.tzinfo
        == timezone.utc
    )


def test_driver_closure():
    def has_chrome_driver_been_found(driver_pid: str) -> bool:
        ps_cmd = Popen(["ps", "-eo", "pid,ppid,args"], stdout=PIPE, stderr=PIPE)
        stdout, _ = ps_cmd.communicate()
        processes = [line.decode().split(maxsplit=2) for line in stdout.splitlines()]

        for pid, ppid, cmdline in processes:
            if pid == driver_pid and "defunct" not in cmdline:
                driver_ppid = ppid
                driver_cmdline = cmdline
                break
        else:
            return False

        for pid, ppid, _ in processes:
            if pid != driver_pid and ppid == driver_ppid and "chrome" in driver_cmdline:
                return True

        return False

    with Driver() as driver:
        driver_pid = str(driver.service.process.pid)
        assert has_chrome_driver_been_found(driver_pid) is True

    assert has_chrome_driver_been_found(driver_pid) is False


def test_driver_tabs_opening():
    vessel_imo = 9175834
    test_vessel = VesselPositionMarineTraffic(IMO=vessel_imo)
    marine_traffic_scrapper = MarineTrafficVesselScraper()
    vessel_url = f"{marine_traffic_scrapper.base_url}{test_vessel.IMO}"
    with Driver() as driver:
        assert len(driver.window_handles) == 1

        for _ in range(2):
            driver.get(vessel_url)

        assert len(driver.window_handles) == 1


def test_speed_field_is_correctly_parsed():
    speed_field_value = "2.2 knots"
    speed_field_value_null = "0.0 knots"
    expected_speed = 2.2
    expected_speed_null = 0
    extracted_speed = MarineTrafficVesselScraper.extract_speed_from_scrapped_field(
        speed_field_value,
    )
    extracted_speed_null = MarineTrafficVesselScraper.extract_speed_from_scrapped_field(
        speed_field_value_null,
    )

    assert extracted_speed == expected_speed
    assert extracted_speed_null == expected_speed_null
