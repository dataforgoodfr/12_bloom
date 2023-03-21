import asyncio
import fnmatch
import functools
from collections.abc import Callable, Coroutine
from os import environ
from pathlib import Path
from typing import Any

import aiofiles
from aiobotocore.session import ClientCreatorContext, get_session
from aiocsv import AsyncWriter
from botocore.exceptions import ClientError


def async_to_sync(coro: Coroutine) -> Callable:
    @functools.wraps(coro)
    def wrapper(storage: "DataStorage", *args: Any, **kwargs: Any) -> Any:
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            async with storage.create_client() as client:
                return await coro(storage, client, *args, **kwargs)

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_wrapper(*args, **kwargs))

    return wrapper


class MissingAWSCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID "
            "environment variables should be defined before running the app.",
        )


class DataStorage:
    def __init__(self) -> None:
        if "AWS_ACCESS_KEY_ID" not in environ or "AWS_SECRET_ACCESS_KEY" not in environ:
            raise MissingAWSCredentialsError()

        self._end_point_url = "https://s3.fr-par.scw.cloud"
        self._bucket_id = "bloom-s3"
        self._cache_path = Path.joinpath(Path.home(), ".s3_cache")
        self._session = get_session()

    def create_client(self) -> ClientCreatorContext:
        return self._session.create_client(
            "s3",
            aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"],
            endpoint_url=self._end_point_url,
        )

    def _get_cache_path(self, path: Path | str) -> Path:
        file_cache_path = Path.joinpath(self._cache_path, path)
        file_cache_path.parent.mkdir(parents=True, exist_ok=True)
        return file_cache_path

    async def _append_row(
        self,
        client: ClientCreatorContext,
        path: Path | str,
        row: list,
    ) -> None:
        cache_path = self._get_cache_path(path)

        if not cache_path.exists():
            async with aiofiles.open(cache_path, "bw") as cache_fd:
                try:
                    data = await self._get_file(client, path)
                except ClientError:
                    pass
                else:
                    await cache_fd.write(data)

        async with aiofiles.open(cache_path, "a", newline="") as cache_fd:
            csv_writer = AsyncWriter(cache_fd)
            await csv_writer.writerow(row)

        async with aiofiles.open(cache_path, "rb") as cache_fd:
            await client.put_object(
                Body=await cache_fd.read(),
                Bucket=self._bucket_id,
                Key=str(path),
            )

    @async_to_sync
    async def append_rows(
        self,
        client: ClientCreatorContext,
        paths: list[Path | str],
        rows: list[list],
    ) -> None:
        await asyncio.gather(
            *[
                self._append_row(client, path, row)
                for path, row in zip(paths, rows, strict=True)
            ],
        )

    async def _get_file(self, client: ClientCreatorContext, path: Path | str) -> bytes:
        s3_object = await client.get_object(Bucket=self._bucket_id, Key=str(path))
        return await s3_object["Body"].read()

    @async_to_sync
    async def get_data(
        self,
        client: ClientCreatorContext,
        paths: list[Path | str],
    ) -> bytes:
        streams = await asyncio.gather(
            *[self._get_file(client, path) for path in paths],
        )

        return b"".join(streams)

    @async_to_sync
    async def glob(self, client: ClientCreatorContext, regex: str) -> list[str]:
        filtered_paths = []

        paginator = client.get_paginator("list_objects_v2")
        async for result in paginator.paginate(Bucket=self._bucket_id):
            for s3_object in result["Contents"]:
                path = s3_object["Key"]

                if fnmatch.fnmatch(path, regex):
                    filtered_paths.append(path)

        return filtered_paths
