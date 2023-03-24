"""This package contains all the infra related code.

Three functions allow us to get ship data from S3 storage.
Each function yield an object than geopandas can read:

>>> import geopandas as geopd
>>> from src.infra import get_vessel_file # ruff remove the import for now,
                                          # have to fix that

>>> file = get_vessel_file(8224418)
>>> df = geopd.read_file(file)
>>> print(df)

Here are the three functions, please use `help(the_function)`
to get more information about them.

def get_data_file(
    vessel_imos: int | str | list[int | str] = None,
    since_date_string: str | None = None,
    until_date_string: str | None = None,
) -> DataFile:

def get_period_file(
    since_date_string: str | None = "24 hours ago",
    until_date_string: str | None = None,
) -> DataFile:
def get_vessel_file(vessel_imo: int | str) -> DataFile

"""
