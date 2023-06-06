
import pandas as pd
from datetime import datetime
from ..vessels.vessel import Vessel
from ..vessels.fleet import Fleet

# Download csv here https://globalfishingwatch.org/data-download/datasets/public-training-data-v1


def load_global_fishing_watch_dataset(path):

    df = pd.read_csv(path)
    # Parse the timestamps to datetime objects
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x))

    # Create a Vessel object for each unique mmsi
    vessels = {}
    for mmsi, vessel_data in df.groupby('mmsi'):
        this_vessel = Vessel(vessel_id = mmsi)
        this_vessel.load_long_lat_from_pandas(vessel_data.reset_index(drop = True).copy())
        vessels[mmsi] = this_vessel

    fleet = Fleet(vessels)

    return fleet,df