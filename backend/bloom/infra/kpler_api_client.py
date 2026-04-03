from bloom.config import settings
from typing import Any
import aiohttp
from urllib.parse import urljoin
from bloom.logger import logger


class KplerApiError(Exception):
    pass

class KplerApiClient:
    FORMAT = 'json'

    def __init__(self):
        self.api_root = settings.kpler_api_root
        self.api_token = settings.kpler_token
        conn = aiohttp.TCPConnector()
        self.http_session = aiohttp.ClientSession(connector=conn)

    async def get(self, endpoint: str, params=None, **kwargs) -> Any:
        if params is None:
            params = {}
        params = params | {"format": KplerApiClient.FORMAT} | kwargs
        headers={"Authorization": "Basic " + self.api_token,
                 "Accept": "application/json"}
        path = urljoin(self.api_root, endpoint)

        logger.debug(f"GET {path}, params={params}")
        async with self.http_session.get(path, params=params, headers=headers) as resp:
            if resp.status == 204:
                return None
            elif resp.ok:
                response = await resp.json()
                return response
            else:
                resp.raise_for_status()

    async def close(self):
        await self.http_session.close()