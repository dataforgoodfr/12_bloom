import asyncio
import csv
import fnmatch
import functools
from collections.abc import Callable, Coroutine
from enum import Enum
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Any

import aiofiles
from aiobotocore.session import ClientCreatorContext, get_session
from aiocsv import AsyncDictWriter
from botocore.exceptions import ClientError, EndpointConnectionError
from pydantic import BaseModel

logger = getLogger()


def async_to_sync(coro: Coroutine) -> Callable:
    """Convert a coroutine to a function."""

    @functools.wraps(coro)
    def wrapper(storage: "DataStorage", *args: Any, **kwargs: Any) -> Any:
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            async with storage.create_client() as client:
                # We are not giving client as an argument to avoid changing
                # methods signature which would make ide information
                # confusing. Methods that are not wrapped explicitely
                # are therefore prefixed with __ to "prevent" their use
                # elsewhere.
                storage.client = client
                result = await coro(storage, *args, **kwargs)
                storage.client = None
                return result

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_wrapper(*args, **kwargs))

    return wrapper


class MissingAWSCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "AWS_SECRET_ACCESS_KEY and AWS_ACCESS_KEY_ID "
            "environment variables should be defined before running the app.",
        )


class StorageType(Enum):
    """Type of bucket storage.

    More information about them can be found there:
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
    """

    STANDARD = 1
    REDUCED_REDUNDANCY = 2
    STANDARD_IA = 3
    ONEZONE_IA = 4
    INTELLIGENT_TIERING = 5
    GLACIER = 6
    DEEP_ARCHIVE = 7
    OUTPOSTS = 8
    GLACIER_IR = 9


class DataStorage:
    """An S3 data storage with methods to append elements and to download csv files.

    It is element agnostic and path almost-agnostic. It has a knowledge
    on path-building to clean outdated cache. This can be improved later on if needed.

    Elements sould be given as BaseModel so that this class is not dependent of any
    of them.

    """

    def __init__(self, storage_type: StorageType = StorageType.STANDARD) -> None:
        if "AWS_ACCESS_KEY_ID" not in environ or "AWS_SECRET_ACCESS_KEY" not in environ:
            raise MissingAWSCredentialsError()

        self._end_point_url = "https://s3.fr-par.scw.cloud"
        self._bucket_id = "bloom-s3"
        self._storage_type = storage_type
        self._cache_path = Path.joinpath(Path.home(), ".s3_cache")
        self._session = get_session()
        self.client = None

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

    def _get_data_storage_path(self, cache_path: Path | str) -> Path:
        storage_path = str(cache_path).removeprefix(str(self._cache_path))
        return Path(storage_path[1:])

    async def _is_s3_object_up_to_date(self, s3_path: Path, cache_path: Path) -> bool:
        s3_object = await self.client.get_object(
            Bucket=self._bucket_id,
            Key=str(s3_path),
        )

        s3_object_last_modif_time = s3_object["LastModified"].timestamp()
        cache_file_last_modif_time = cache_path.lstat().st_mtime

        return s3_object_last_modif_time >= cache_file_last_modif_time

    async def _clean_outdated_cache(self, path: Path) -> None:
        """Clean outdated cache files.

        This method depends on the way cache files are stored.
        Be carefull if changed are made in SplitVesselRepository.
        """

        for cache_path in path.parent.iterdir():
            if cache_path == path:
                continue

            storage_path = self._get_data_storage_path(cache_path)

            if await self._is_s3_object_up_to_date(storage_path, cache_path):
                cache_path.unlink()
            else:
                async with aiofiles.open(cache_path, "rb") as cache_fd:
                    try:
                        await self.client.put_object(
                            Body=await cache_fd.read(),
                            Bucket=self._bucket_id,
                            Key=str(storage_path),
                            StorageClass=self._storage_type.name,
                        )
                    except EndpointConnectionError:
                        logger.exception("Failed to push data on scaleway.")
                    else:
                        cache_path.unlink()

    async def __append_element(
        self,
        path: Path | str,
        element: BaseModel,
    ) -> None:
        cache_path = self._get_cache_path(path)

        await self._clean_outdated_cache(cache_path)
        if not cache_path.exists():
            async with aiofiles.open(cache_path, "w") as cache_fd:
                try:
                    data = await self.__get_file(path)
                except ClientError:
                    writer = AsyncDictWriter(
                        cache_fd,
                        element.__fields__,
                        quoting=csv.QUOTE_ALL,
                    )
                    await writer.writeheader()
                else:
                    await cache_fd.write(data.decode("utf-8"))

        async with aiofiles.open(cache_path, "a", newline="") as cache_fd:
            writer = AsyncDictWriter(
                cache_fd,
                element.__fields__,
                quoting=csv.QUOTE_ALL,
            )
            await writer.writerow(element.dict())

        async with aiofiles.open(cache_path, "rb") as cache_fd:
            try:
                await self.client.put_object(
                    Body=await cache_fd.read(),
                    Bucket=self._bucket_id,
                    Key=str(path),
                    StorageClass=self._storage_type.name,
                )
            except EndpointConnectionError:
                logger.exception("Failed to push data on scaleway.")

    @async_to_sync
    async def append_elements(
        self,
        paths: list[Path | str],
        elements: list[BaseModel],
    ) -> None:
        await asyncio.gather(
            *[
                self.__append_element(path, element)
                for path, element in zip(paths, elements, strict=True)
            ],
        )

    async def __get_file(self, path: Path | str) -> bytes:
        s3_object = await self.client.get_object(Bucket=self._bucket_id, Key=str(path))
        return await s3_object["Body"].read()

    @async_to_sync
    async def get_data(
        self,
        paths: list[Path | str],
    ) -> bytes:
        streams = await asyncio.gather(
            *[self.__get_file(path) for path in paths],
        )

        result = streams.pop(0)
        for stream in streams:
            result += b"".join(stream.split(b"\n")[1:])

        return result

    @async_to_sync
    async def glob(self, regex: str) -> list[str]:
        filtered_paths = []

        paginator = self.client.get_paginator("list_objects_v2")
        async for result in paginator.paginate(Bucket=self._bucket_id):
            for s3_object in result["Contents"]:
                path = s3_object["Key"]

                if fnmatch.fnmatch(path, regex):
                    filtered_paths.append(path)

        return filtered_paths
