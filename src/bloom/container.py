from dependency_injector import containers, providers

from bloom.config import settings
from bloom.infra.database.database_manager import Database
from bloom.infra.repositories.repository_alert import RepositoryAlert
from bloom.infra.repositories.repository_raster import RepositoryRaster
from bloom.infra.repositories.repository_vessel import RepositoryVessel
from bloom.usecase.GenerateAlerts import GenerateAlerts
from bloom.usecase.GetVesselsFromSpire import GetVesselsFromSpire


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

    raster_repository = providers.Factory(
        RepositoryRaster,
        session_factory=db.provided.session,
    )

    get_spire_data_usecase = providers.Factory(
        GetVesselsFromSpire,
        vessel_repository=vessel_repository,
    )

    generate_alert_usecase = providers.Factory(
        GenerateAlerts,
        alert_repository=alert_repository,
        raster_repository=raster_repository,
    )
