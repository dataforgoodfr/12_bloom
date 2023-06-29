from container import UseCases
from bloom.domain.alert import Alert
from datetime import datetime, timezone

test_alert = Alert(
    "ship_name",
    622768943,
    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "position",
    "iucn_cat",
    "mpa_name",
)


def test_launch_alert():

    use_cases = UseCases()
    alert_usecase = use_cases.generate_alert_usecase()
    alert_usecase.send_slack_alert(
        test_alert,
        "THIS IS A TEST",
    )
