
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
        vessels[mmsi] = Vessel(vessel_data.reset_index(drop = True).copy(),mmsi)

    fleet = Fleet(vessels)

    return fleet,df