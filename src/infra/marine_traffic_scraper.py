import contextlib

import undetected_chromedriver as uc
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from time import sleep
from datetime import datetime, timezone
from logging import getLogger

from src.domain.vessel import Vessel

logger = getLogger()

class DriverIsNotInitialized(Exception):
    """This error is raised when using the scrapper outside of a driver context."""


class MarineTrafficVesselScraper:
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.marinetraffic.com/en/data/?asset_type=" \
                        "vessels&columns=shipname,imo,time_of_latest_position," \
                        "lat_of_latest_position,lon_of_latest_position,status," \
                        "speed,navigational_status&quicksearch|begins|quicksearch="

    @contextlib.contextmanager
    def driver_session(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        self.driver = uc.Chrome(options=options, version_main=109)

        yield
        
        self.driver.quit()
        self.driver = None

    def scrap_vessel(self, vessel: Vessel):
        if not self.driver:
            raise DriverIsNotInitialized("This method can only be used in a driver context.")
        
        logger.info(f"Currently scrapping {vessel}")
        crawling_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        vessel_url = f"https://www.marinetraffic.com/en/data/?asset_type=" \
                     f"vessels&columns=shipname,imo,time_of_latest_position," \
                     f"lat_of_latest_position,lon_of_latest_position,status," \
                     f"speed,navigational_status&quicksearch|begins|quicksearch={vessel.IMO}"
        self.driver.get(vessel_url)

        sleep(5)  # wait for the page to load

        try:
            WebDriverWait(self.driver, 5).until(lambda d: d.find_element(By.CLASS_NAME, "ag-body"))
            record = self.driver.find_element(By.CLASS_NAME, "ag-body")
            record_fields = record.text.split('\n')
            if record_fields[1] != vessel.IMO:
                logger.warning(f"IMO has changed: new value {record_fields[1]} vs old value {vessel.IMO}")
            return Vessel(
                timestamp=crawling_timestamp,
                ship_name=record_fields[0],
                IMO=record_fields[1],
                last_position_time=record_fields[2],
                latitude=record_fields[3],
                longitude=record_fields[4]
            )
        except WebDriverException as e:
            logger.error(f"Scrapping failed for vessel {vessel.IMO}")
            logger.error(e)
            return Vessel(
                timestamp=crawling_timestamp,
                ship_name=None,
                IMO=vessel.IMO,
                last_position_time=None,
                latitude=None,
                longitude=None
            )
