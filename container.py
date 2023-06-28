from dependency_injector import containers, providers

from bloom.config import settings
from bloom.infra.database.database_manager import Database
from bloom.infra.http.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repositories.repository_alert import RepositoryAlert
from bloom.infra.repositories.repository_vessel import RepositoryVessel
from bloom.usecase.GenerateAlerts import GenerateAlerts
from bloom.usecase.GetVesselsFromSpire import GetVesselsFromSpire
from bloom.usecase.ScrapVesselsFromMarineTraffic import ScrapVesselsFromMarineTraffic


class UseCases(containers.DeclarativeContainer):
    config = providers.Configuration()
    db_url = settings.db_url
    db = providers.Singleton(
        Database,
        db_url=db_url,
    )

    vessel_repository = providers.Factory(
        RepositoryVessel,
        session_factory=db.provided.session,
    )

    alert_repository = providers.Factory(
        RepositoryAlert,
        session_factory=db.provided.session,
    )

    marine_traffic_scrapper = providers.Factory(
        MarineTrafficVesselScraper,
    )

    scrap_marine_data_usecase = providers.Factory(
        ScrapVesselsFromMarineTraffic,
        vessel_repository=vessel_repository,
        scraper=marine_traffic_scrapper,
    )

    get_spire_data_usecase = providers.Factory(
        GetVesselsFromSpire,
        vessel_repository=vessel_repository,
    )

    generate_alert_usecase = providers.Factory(
        GenerateAlerts,
        alert_repository=alert_repository,
    )
