import os
from datetime import datetime

from shapely import Point
from slack_sdk.webhook import WebhookClient

from bloom.domain.alert import Alert
from bloom.infra.repositories.repository_alert import RepositoryAlert
from bloom.infra.repositories.repository_raster import RepositoryRaster
from bloom.logger import logger


class GenerateAlerts:
    def __init__(
        self,
        alert_repository: RepositoryAlert,
        raster_repository: RepositoryRaster,
    ) -> None:
        self.alert_repository: RepositoryAlert = alert_repository
        self.raster_repository: RepositoryAlert = raster_repository

    def get_distance_shore(self, point: Point) -> None:
        return self.raster_repository.select_distance_shore(point)

    def generate_alerts(self, timestamp: datetime) -> None:
        self.alert_repository.save_alerts(timestamp)

        list_alert = self.alert_repository.load_alert(timestamp)
        for alert in list_alert:
            self.send_slack_alert(alert)

        return

    def send_slack_alert(
        self,
        alert: Alert,
        type_name: str = "Vessel in a Protected Area",
    ) -> int:
        slack_url = os.environ.get("SLACK_URL")
        webhook = WebhookClient(slack_url)
        blocks = (
            """[
                {
                        "type": "header",
                        "text": {
                                "type": "plain_text",
                                "text": "New Alert : """
            + type_name
            + """",
                                "emoji": true
                         }
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
                                        "text": "*Name of the vessel:*\\n"""
            + (alert.ship_name or "None")
            + """"
                                },
                                {
                                        "type": "mrkdwn",
                                        "text": "*Name of the area:*\\n"""
            + alert.mpa_name
            + """"
                                }
                        ]
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
                                        "text": "*When:*\\n"""
            + alert.last_position_time.strftime("%m/%d/%Y, %H:%M:%S")
            + """"
                                },
                                {
                                        "type": "mrkdwn",
                                        "text": "*IUCN category:*\\n"""
            + alert.iucn_cat
            + """"
                                }
                        ]
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
            "text": "*Position of the vessel (Long,Lat):*\\n"""
            + alert.position
            + """"
                                },
                                {
                                        "type": "mrkdwn",
"text": "<https://www.marinetraffic.com/en/data?asset_type=vessels&mmsi%7Ceq%7Cmmsi="""
            + str(alert.mmsi)
            + """|mmsi:>\\n"""
            + str(alert.mmsi)
            + """"
                                }
                        ]
                }
        ]"""
        )
        response = webhook.send(text="fallback", blocks=blocks)

        logger.info(f"Currently sending an alert about this vessel: {alert.ship_name}")
        logger.info(response.status_code)
        return response.status_code
