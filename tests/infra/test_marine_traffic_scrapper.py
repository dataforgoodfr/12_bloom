from domain.vessel import Vessel
from infra.marine_traffic_scraper import MarineTrafficVesselScraper, Driver
from datetime import timezone
from subprocess import Popen, PIPE

def test_scrapper_uses_local_time_in_same_timezone_as_scrapped_time():
    vessel_imo = 9175834
    test_vessel = Vessel(IMO=vessel_imo)
    marine_traffic_scrapper = MarineTrafficVesselScraper()

    with Driver() as driver:
        scrapped_vessel = marine_traffic_scrapper.scrap_vessel(
            driver=driver, 
            vessel=test_vessel
        )

    assert scrapped_vessel.last_position_time.tzinfo == scrapped_vessel.timestamp.tzinfo == timezone.utc


def test_driver_closure():
    def has_chrome_driver_been_found(driver_pid: int) -> bool:
        ps_cmd = Popen(['ps', '-eo' ,'pid,ppid,args'], stdout=PIPE, stderr=PIPE)
        stdout, _ = ps_cmd.communicate()
        processes = [
            line.decode().split(maxsplit=2)
            for line in stdout.splitlines()
        ]

        for pid, ppid, cmdline  in processes:
            if pid == driver_pid and "defunct" not in cmdline:
                driver_ppid = ppid
                break
        else:
            return False
        
        for pid, ppid, cmdline in processes:
            if pid != driver_pid and ppid == driver_ppid and "chrome" in cmdline:
                return True
        
        return False
    

    with Driver() as driver:
        driver_pid = str(driver.service.process.pid)
        
        assert has_chrome_driver_been_found(driver_pid) is True
    
    assert has_chrome_driver_been_found(driver_pid) is False


def test_driver_tabs_opening():
    vessel_imo = 9175834
    test_vessel = Vessel(IMO=vessel_imo)
    marine_traffic_scrapper = MarineTrafficVesselScraper()

    with Driver() as driver:
        assert len(driver.window_handles) == 1

        for _ in range(2):
            marine_traffic_scrapper.scrap_vessel(
                driver=driver, 
                vessel=test_vessel
            )

        assert len(driver.window_handles) == 1