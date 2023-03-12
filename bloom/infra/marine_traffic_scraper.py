from datetime import datetime, timezone
from logging import getLogger
from time import sleep

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome, ChromeOptions

from bloom.domain.vessel import Vessel

logger = getLogger()


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
            version_main=109,
        )
        return self._driver

    def __exit__(self, exc_type: str, exc_value: str, exc_traceback: str) -> None:
        self._driver.quit()


class MarineTrafficVesselScraper:
    def __init__(self) -> None:
        self.base_url = (
            "https://www.marinetraffic.com/en/data/?asset_type="
            "vessels&columns=shipname,imo,time_of_latest_position,"
            "lat_of_latest_position,lon_of_latest_position,status,"
            "speed,navigational_status&quicksearch|begins|quicksearch="
        )

    def scrap_vessel(self, driver: Driver, vessel: Vessel) -> Vessel:
        logger.info(f"Currently scrapping {vessel}")

        crawling_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        vessel_url = f"{self.base_url}{vessel.IMO}"
        driver.get(vessel_url)

        sleep(5)  # wait for the page to load

        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.find_element(By.CLASS_NAME, "ag-body"),
            )
            record = driver.find_element(By.CLASS_NAME, "ag-body")
            record_fields = record.text.split("\n")
            if record_fields[1] != vessel.IMO:
                logger.warning(
                    "IMO has changed: "
                    f"new value {record_fields[1]} vs old value {vessel.IMO}",
                )
                vessel_records = Vessel(
                    timestamp=crawling_timestamp,
                    ship_name=None,
                    IMO=vessel.IMO,
                    last_position_time=None,
                    latitude=None,
                    longitude=None,
                )
            else:
                vessel_records = Vessel(
                    timestamp=crawling_timestamp,
                    ship_name=record_fields[0],
                    IMO=record_fields[1],
                    last_position_time=record_fields[2],
                    latitude=record_fields[3],
                    longitude=record_fields[4],
                )
        except WebDriverException:
            logger.exception(f"Scrapping failed for vessel {vessel.IMO}")
            vessel_records = Vessel(
                timestamp=crawling_timestamp,
                ship_name=None,
                IMO=vessel.IMO,
                last_position_time=None,
                latitude=None,
                longitude=None,
            )
        return vessel_records
