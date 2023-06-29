from container import UseCases
from bloom.domain.alert import Alert
from datetime import datetime, timezone


def test_launch_alert():

    use_cases = UseCases()
    alert_usecase = use_cases.generate_alert_usecase()
    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    alert_usecase.send_slack_alert(
        Alert("ship_name", 622768943, "position", "iucn_cat", "mpa_name"),
        "THIS IS A TEST",
    )
