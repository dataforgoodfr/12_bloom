import json

from bloom.config import settings
from bloom.infra.repositories.repository_port import PortRepository


class PortUseCase:
    def __init__(self, ports_repository: PortRepository, redis_client):
        self.ports_repository = ports_repository
        self.redis_client = redis_client
        self.caching_key = 'ports:caching'

    async def list_ports(self):
        ports = self.ports_repository.get_all_ports()
        await self.redis_client.set(self.caching_key, json.dumps(ports))
        await self.redis_client.expire(self.caching_key, settings.redis_cache_expiration)
        return ports

    async def get_port_by_id(self, port_id):
        return self.ports_repository.get_port_by_id(port_id)
