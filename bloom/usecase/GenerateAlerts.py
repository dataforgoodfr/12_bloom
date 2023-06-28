from datetime import datetime

from bloom.infra.repositories.repository_alert import RepositoryAlert


class GenerateAlerts:
    def __init__(
        self,
        alert_repository: RepositoryAlert,
    ) -> None:
        self.alert_repository: RepositoryAlert = alert_repository

    def generate_alerts(self, timestamp: datetime) -> None:

        self.alert_repository.save_alerts(timestamp)

        self.alert_repository.load_alert(timestamp)

        return
