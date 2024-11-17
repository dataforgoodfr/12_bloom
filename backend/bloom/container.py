from bloom.config import settings
from bloom.infra.database.database_manager import Database
from bloom.infra.repositories.repository_alert import RepositoryAlert
from bloom.infra.repositories.repository_excursion import ExcursionRepository
from bloom.infra.repositories.repository_port import PortRepository
from bloom.infra.repositories.repository_raster import RepositoryRaster
from bloom.infra.repositories.repository_spire_ais_data import SpireAisDataRepository
from bloom.infra.repositories.repository_vessel import VesselRepository
from bloom.infra.repositories.repository_vessel_position import VesselPositionRepository
from bloom.infra.repositories.repository_segment import SegmentRepository
from bloom.infra.repositories.repository_zone import ZoneRepository
from bloom.services.GetVesselsFromSpire import GetVesselsFromSpire
from bloom.services.metrics import MetricsService
from bloom.usecase.GenerateAlerts import GenerateAlerts
from dependency_injector import containers, providers
import redis


class UseCases(containers.DeclarativeContainer):
    config = providers.Configuration()
    db_url = settings.db_url
    db = providers.Singleton(
        Database,
        db_url=db_url,
    )

    vessel_repository = providers.Factory(
        VesselRepository,
    )

    alert_repository = providers.Factory(
        RepositoryAlert,
        session_factory=db.provided.session,
    )

    raster_repository = providers.Factory(
        RepositoryRaster,
        session_factory=db.provided.session,
    )

    port_repository = providers.Factory(
        PortRepository,
        session_factory=db.provided.session,
    )

    zone_repository = providers.Factory(
        ZoneRepository,
        session_factory=db.provided.session,
    )

    excursion_repository = providers.Factory(
        ExcursionRepository,
        session_factory=db.provided.session,
    )

    vessel_position_repository = providers.Factory(
        VesselPositionRepository,
        session_factory=db.provided.session,
    )

    get_spire_data_usecase = providers.Factory(GetVesselsFromSpire)

    generate_alert_usecase = providers.Factory(
        GenerateAlerts,
        alert_repository=alert_repository,
        raster_repository=raster_repository,
    )

    spire_ais_data_repository = providers.Factory(
        SpireAisDataRepository,
        session_factory=db.provided.session,
    )

    segment_repository = providers.Factory(
        SegmentRepository,
        session_factory=db.provided.session,
    )

    metrics_service = providers.Factory(
        MetricsService,
        session_factory=db.provided.session,
    )
