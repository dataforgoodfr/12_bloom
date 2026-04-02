from bloom.container import UseCases
from bloom.domain.alert import Alert
from datetime import datetime, timezone

test_alert = Alert(
    ship_name="ship_name",
    mmsi=622768943,
    last_position_time=datetime.now(timezone.utc),
    position="position",
    iucn_cat="iucn_cat",
    mpa_name="mpa_name",
)


def test_launch_alert():
    use_cases = UseCases()
    alert_usecase = use_cases.generate_alert_usecase()
    status_code = alert_usecase.send_slack_alert(
        test_alert,
        "THIS IS A TEST",
    )
    assert status_code == 404
