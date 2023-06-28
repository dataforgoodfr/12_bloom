import os
from datetime import datetime
from slack_sdk.webhook import WebhookClient
from bloom.infra.repositories.repository_alert import RepositoryAlert
from bloom.domain.alert import Alert

class GenerateAlerts:
    def __init__(
        self,
        alert_repository: RepositoryAlert,
    ) -> None:
        self.alert_repository: RepositoryAlert = alert_repository

    def generate_alerts(self, timestamp: datetime) -> None:

        self.alert_repository.save_alerts(timestamp)

        list_alert = self.alert_repository.load_alert(timestamp)
        for alert in list_alert:
            self.send_slack_alert(alert)

        return

    def send_slack_alert(self, alert: Alert) -> None:

        slack_url = os.environ.get("SLACK_URL")

        webhook = WebhookClient(slack_url)
        print("send a message")
        blocks='''[
                {
                        "type": "header",
                        "text": {
                                "type": "plain_text",
                                "text": "New Alert : Vessel in a Protected Area",
                                "emoji": true
                         }
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
                                        "text": "*Name of the vessel:*\\n''' + alert.ship_name + '''"
                                },
                                {
                                        "type": "mrkdwn",
                                        "text": "*Name of the area:*\\n''' + alert.mpa_name + '''"
                                }
                        ]
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
                                        "text": "*When:*\\n''' + alert.last_position_time.strftime("%m/%d/%Y, %H:%M:%S") + '''"
                                },
                                {
                                        "type": "mrkdwn",
                                        "text": "*IUCN category:*\\n''' + alert.iucn_cat + '''"
                                }
                        ]
                },
                {
                        "type": "section",
                        "fields": [
                                {
                                        "type": "mrkdwn",
                                        "text": "*Position of the vessel:*\\n''' + alert.position + '''"
                                },
                                {
                                        "type": "mrkdwn",
                                        "text": "*mmsi:*\\n''' + str(alert.mmsi) + '''"
                                }
                        ]
                }
        ]'''
        print(blocks)
        response = webhook.send(text="fallback",blocks=blocks)
        print(response.status_code)
        print(response.body)
        #assert response.status_code == 200
        #assert response.body == "ok"
