import os
import re
from datetime import datetime, timezone
from logging import getLogger
from time import sleep

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from shapely import Point
from undetected_chromedriver import Chrome, ChromeOptions

from bloom.domain.vessel import Vessel, VesselPositionMarineTraffic

logger = getLogger()
version = os.popen("/usr/bin/google-chrome --version")  # nosec
version_chrome = version.read().strip().split()[-1]
CHROME_VERSION = int(version_chrome.split(".")[0])


class Driver:
    def __init__(
        self,
    ) -> None:
        arguments = [
            "--disable-extensions",
            "--disable-application-cache",
            "--disable-gpu",
            "--headless=new",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--headless",
        ]
        self._options = ChromeOptions()

        for arg in arguments:
            self._options.add_argument(arg)

    def __enter__(self) -> Chrome:
        self._driver = Chrome(
            options=self._options,
            version_main=CHROME_VERSION,
        )
        return self._driver

    def __exit__(self, exc_type: str, exc_value: str, exc_traceback: str) -> None:
        self._driver.quit()


class MarineTrafficVesselScraper:
    def __init__(self) -> None:
        self.base_url = (
            "https://www.marinetraffic.com/en/data/?asset_type="
            "vessels&columns=shipname,current_port,imo,mmsi,"
            "time_of_latest_position,lat_of_latest_position,"
            "lon_of_latest_position,status,speed,navigational_status"
            "&quicksearch|begins|quicksearch="
        )

    def scrap_vessels(self, vessels: list[Vessel]) -> list[VesselPositionMarineTraffic]:
        with Driver() as driver:
            vessels_list = []
            for vessel in vessels:
                logger.info(f"Currently scrapping {vessel}")

                crawling_timestamp = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M UTC",
                )
                vessel_url = f"{self.base_url}{vessel.IMO}"
                driver.get(vessel_url)

                sleep(2)  # wait for the page to load

                try:
                    WebDriverWait(driver, 5).until(
                        lambda d: d.find_element(By.CLASS_NAME, "ag-body"),
                    )
                    record = driver.find_element(By.CLASS_NAME, "ag-body")
                    record_fields = record.text.split("\n")
                    if record_fields == [""]:
                        logger.warning(
                            f"IMO {vessel.IMO} not avaiable on MarineTraffic",
                        )
                        continue
                    if record_fields[2] != vessel.IMO:
                        logger.warning(
                            "IMO has changed: "
                            f"new value {record_fields[1]} vs old value {vessel.IMO}",
                        )
                    if record_fields[5] == "-" or record_fields[6] == "-":
                        logger.warning(
                            f"No position data available for this IMO {vessel.IMO}, "
                            f"{record_fields}",
                        )
                        continue
                except WebDriverException:
                    logger.exception(
                        f"Scrapping failed for vessel {vessel.IMO}, "
                        f"with exception {WebDriverException.__name__}",
                    )
                    vessels_list.append(
                        VesselPositionMarineTraffic(
                            vessel_id=vessel.vessel_id,
                            ship_name=vessel.ship_name,
                            timestamp=crawling_timestamp,
                            IMO=vessel.IMO,
                        ),
                    )
                else:
                    logger.warning(
                        f"Scrapping {record_fields[2]}",
                    )
                    logger.warning(
                        f"With result {record_fields}",
                    )
                    vessels_list.append(
                        VesselPositionMarineTraffic(
                            timestamp=crawling_timestamp,
                            ship_name=record_fields[0],
                            current_port=record_fields[1],
                            IMO=record_fields[2],
                            vessel_id=vessel.vessel_id,
                            mmsi=record_fields[3],
                            last_position_time=record_fields[4],
                            at_port=self._is_at_port(record_fields[1]),
                            position=Point(record_fields[5], record_fields[6]),
                            status=record_fields[7],
                            speed=self._extract_speed_from_scrapped_field(
                                record_fields[8],
                            ),
                            navigation_status=record_fields[7],
                            fishing=self._is_fishing(record_fields[7]),
                        ),
                    )
        return vessels_list

    @staticmethod
    def _extract_speed_from_scrapped_field(speed_field: str) -> float | None:
        speed = re.findall(r"[\d]*[.][\d]*", speed_field)
        if len(speed) > 0:
            return float(speed[0])
        return None

    @staticmethod
    def _is_fishing(navigation_status: str) -> bool:
        return "fishing" in navigation_status.lower()

    @staticmethod
    def _is_at_port(current_port: str) -> bool:
        return "-" not in current_port
