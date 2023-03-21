"""DataFiles makes it easy to use by data scientists. """

import functools
import inspect
import zipfile
from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any

from bloom.infra.data_storage import DataStorage


class DataDoesNotExistError(Exception):
    "Error triggered when no data matchs a filter"

    def __init__(self) -> None:
        super().__init__("No data has been found with the given filter.")


class DataFile(BytesIO):
    """A mock file agnostic to the csv split method."""

    def __init__(self, csv_paths: list[Path]) -> None:
        self._csv_paths = csv_paths
        self._storage = DataStorage()
        self._is_initialized = False

        self._add_context_to_reading_methods()

    def _add_context_to_reading_methods(self) -> None:
        """Add a context aware data loader at each reading method.

        As the context is only known when the reading action
        occurs, the data is loaded at this moment. All the read methods
        are therefore augmented to load the data if it has not been done
        previously.
        """

        for method_name in dir(self):
            if method_name.startswith(("read", "get")):
                method = getattr(self, method_name)
                method = self._add_context_aware_loader(method)
                setattr(self, method_name, method)

    def _load_as_plain(self) -> None:
        """Load a plain csv file."""
        data = self._storage.get_data(self._csv_paths)
        self.write(data)

    def _load_as_zip(self) -> None:
        """Load zipfile data.

        This method is used when reading a file with Geopandas.
        Geopandas only handles zip files when reading bytes for now.
        """

        with zipfile.ZipFile(self, "w") as z:
            data = self._storage.get_data(self._csv_paths)
            z.writestr("data.csv", data)

    def _load_data(self) -> None:
        """Loads data depending on the context.

        This method loads a content tailored to the reader.
        """

        current_frame, read_frame, caller_frame, *parent_frames = inspect.stack()

        if "geopandas" in caller_frame.filename:
            self._load_as_zip()
        else:
            self._load_as_plain()

        self.seek(0)
        self._is_initialized = True

    def _add_context_aware_loader(self, read_method: Callable) -> Callable:
        """Decorator that loads data before each first reading."""

        @functools.wraps(read_method)
        def read_wrapper(*args: Any, **kwargs: Any) -> bytes:
            if not self._is_initialized:
                self._load_data()

            return read_method(*args, **kwargs)

        return read_wrapper
