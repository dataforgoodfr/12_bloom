import json

from bloom.config import settings
from bloom.logger import logger


class ExcursionUseCase:
    def __init__(self, excursions_repository, redis_client):
        self.excursions_repository = excursions_repository
        self.redis_client = redis_client
        self.endpoint = f"/vessels/excursions"

    def list_vessel_excursions(self, vessel_id, with_cache=True):
        return self.excursions_repository.get_vessel_excursions(vessel_id, with_cache)

    async def get_excursions_by_vessel_id(self, vessel_id):
        excursions = self.excursions_repository.get_excursions_by_vessel_id(vessel_id)

        await self.redis_client.set(self.endpoint, json.dumps(excursions))
        await self.redis_client.expire(self.endpoint, settings.redis_cache_expiration)
        return self.excursions_repository.get_excursions_by_vessel_id(vessel_id)

    async def get_excursion_by_id(self, vessel_id, excursions_id):
        return self.excursions_repository.get_excursion_by_id(vessel_id, excursions_id)

    async def get_excursions_segments(self, vessel_id, excursions_id, segment_id):
        return self.excursions_repository.get(vessel_id, excursions_id, segment_id)

    async def get_segment_by_id(self, vessel_id, excursions_id, segment_id):
        return self.excursions_repository.get_segment_by_id(vessel_id, excursions_id, segment_id)
