"""This package contains all the infra related code.

Three functions allow us to get ship data from S3 storage.
Each function yield an object than geopandas can read:

>>> import geopandas as geopd
>>> from src.infra import get_vessel_file

>>> file = get_vessel_file(8224418)
>>> df = geopd.read_file(file)
>>> print(df)

Here are the three functions, please use `help(the_function)`
to get more information about them.

def get_data_file(
    vessel_imos: int | str | list[int | str] = None,
    date_strings: list[str] | str = None,
) -> DataFile

def get_day_file(date_string: str = "today") -> DataFile
def get_vessel_file(vessel_imo: int | str) -> DataFile

"""
