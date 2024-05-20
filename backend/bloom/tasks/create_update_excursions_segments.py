import argparse
from datetime import timedelta, datetime
from time import perf_counter

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from geopy import distance
from shapely.geometry import Point

from bloom.container import UseCases
from bloom.domain.vessel_position import VesselPosition
from bloom.domain.segment import Segment
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.logger import logger
from bloom.tasks.create_new_excursion import add_excursion, close_excursion, update_excursion

import warnings

warnings.filterwarnings("ignore")


def get_distance(current_position: tuple, last_position: tuple):
    if np.isnan(last_position[0]) or np.isnan(last_position[1]):
        return np.nan

    return distance.geodesic(current_position, last_position).km


def map_vessel_position_to_domain(row: pd.Series) -> VesselPosition:
    return VesselPosition(
        vessel_id=row["vessel_id"],
        timestamp=row["position_timestamp"],
        accuracy=row["position_accuracy"],
        collection_type=row["position_collection_type"],
        course=row["position_course"],
        heading=row["position_heading"],
        position=Point(row["position_longitude"], row["position_latitude"]),
        latitude=row["position_latitude"],
        longitude=row["position_longitude"],
        maneuver=row["position_maneuver"],
        navigational_status=row["position_navigational_status"],
        rot=row["position_rot"],
        # speed=row["position_speed"],
        speed=row["speed"],
    )


def to_coords(row: pd.Series) -> pd.Series:
    if pd.isna(row["end_position"]) is False:
        row["longitude"] = row["end_position"].x
        row["latitude"] = row["end_position"].y

    return row


def run(batch_time):
    use_cases = UseCases()
    db = use_cases.db()
    spire_repository = use_cases.spire_ais_data_repository()
    excursion_repository = use_cases.excursion_repository()
    segment_repository = use_cases.segment_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    vessel_repository = use_cases.vessel_repository()

    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "create_update_excursions_segments"
        )
        # TaskExecutionRepository.set_point_in_time(session, "create_update_excursions_segments", max_created)
        # logger.info(f"Ecriture de {len(clean_positions)} positions dans la table vessel_positions")
        session.commit()

    return
    # Step 10: segment and excursion creation
    # minimal distance to consider a vessel being in a port (in meters)
    threshold_distance_to_port = 5000
    # maximal average speed of a vessel to check if it's in a port (in knot)
    maximal_speed_to_check_if_in_port = 0.1
    # average speed to take when vessel exit a port (in knot/h)
    average_exit_speed = 7

    # process for each unique mmsi
    ongoing_excursion_id = np.NaN
    open_ongoing_excursion = True
    result = pd.DataFrame()
    for mmsi in batch['vessel_mmsi'].unique():
        # if (1==1): # temp, used to test on only 1 mmsi ; to remove when finished
        # mmsi = 227143600 # temp, used to test on only 1 mmsi ; to remove when finished
        # print('MMSI : '+str(mmsi))
        # getting data for a given mmsi and assign them to the end point of a segment
        df_end = batch.loc[
            batch['vessel_mmsi'] == mmsi, ['vessel_mmsi', 'position_timestamp', 'position_heading', 'position_speed',
                                           'position_longitude', 'position_latitude']].copy()
        # getting vessel_id
        with db.session() as session:
            vessel = vessel_repository.get_activated_vessel_by_mmsi(session, int(mmsi))
            vessel_id = vessel.id
            session.commit()
        # rename columns to match segment table structure
        df_end.rename(columns={'vessel_mmsi': 'mmsi',
                               'position_timestamp': 'timestamp_end',
                               'position_heading': 'heading_at_end',
                               'position_speed': 'speed_at_end',
                               'position_longitude': 'end_longitude',
                               'position_latitude': 'end_latitude'
                               }, inplace=True)
        # sort chronologically and reset index
        df_end.sort_values('timestamp_end', inplace=True)
        df_end.reset_index(drop=True, inplace=True)
        # get every end entry but the last one ; each one of them will be the start point of a segment
        df_start = df_end.iloc[0:-1, :].copy()
        # rename columns to match segment table structure
        for col in df_start.columns:
            df_start.rename(columns={col: col.replace('end', 'start')}, inplace=True)
        # get the end position of the last segment of the vessel ; this will become the start point of the first new segment
        if (last_segment.shape[0] > 0):
            vessel_last_segment = last_segment.loc[
                last_segment['mmsi'] == mmsi, ['mmsi', 'timestamp_end', 'heading_at_end', 'speed_at_end',
                                               'end_position', 'excursion_id', 'arrival_port_id']]
            vessel_last_segment['start_latitude'] = vessel_last_segment['end_position'].apply(lambda x: x.y)
            vessel_last_segment['start_longitude'] = vessel_last_segment['end_position'].apply(lambda x: x.x)
            vessel_last_segment.drop('end_position', inplace=True, axis=1)
            vessel_last_segment.rename(columns={'timestamp_end': 'timestamp_start',
                                                'heading_at_end': 'heading_at_start',
                                                'speed_at_end': 'speed_at_start'
                                                }, inplace=True)
        else:
            vessel_last_segment = pd.DataFrame()

        if (vessel_last_segment.shape[0] > 0):
            # if there's a last segment for this vessel, then it's not the first time a position for this vessel is received
            is_new_vessel = False
            # and it becomes the start point of the first new segment
            df_start.loc[-1] = vessel_last_segment.loc[0]
            print(df_start)
            df_start.sort_index(inplace=True)
            df_start.reset_index(drop=True, inplace=True)
            # checks if the excursion of the last segment is closed or not
            if (vessel_last_segment['arrival_port_id'].iloc[0] >= 0):
                open_ongoing_excursion = False
            else:
                open_ongoing_excursion = True
                ongoing_excursion_id = vessel_last_segment['excursion_id'].iloc(0).values

        else:
            # if there's no last segment for this vessel, then it's the first time a position for this vessel is received
            is_new_vessel = True
            # so we duplicate the starting point to have the first segment while setting it up 1s behind in time (so timestamp_start != timestamp_end)
            df_start.loc[-1] = df_start.loc[0]
            df_start['timestamp_start'].iloc[-1] += timedelta(0, -1)
            df_start.sort_index(inplace=True)
            df_start.reset_index(drop=True, inplace=True)
            open_ongoing_excursion = False

        # concat start and end point together
        df = pd.concat([df_start, df_end], axis=1)

        # removing segment with same timestamp_start and timestamp_end (no update)
        df = df[df['timestamp_start'] != df['timestamp_end']].copy()
        # reseting index
        df.reset_index(inplace=True, drop=True)

        if (df.shape[0] > 0):
            # calculate distance
            def get_distance_in_miles(x):
                p1 = (x.start_latitude, x.start_longitude)
                p2 = (x.end_latitude, x.end_longitude)
                return distance.distance(p1, p2).km / 1.852

            df['distance'] = df.apply(get_distance_in_miles, axis=1)

            # calculate duration in seconds
            def get_duration(x):
                return (x.timestamp_end - x.timestamp_start).total_seconds()

            df['segment_duration'] = df.apply(get_duration, axis=1)

            # set default type as AT_SEA
            df['type'] = 'AT_SEA'

            # set type as default_ais for segment with duration > 35 min
            df.loc[df['segment_duration'] >= 2100, 'type'] = 'DEFAULT_AIS'

            # calculate average speed in knot
            df.loc[df['type'] != 'DEFAULT_AIS', 'average_speed'] = df['distance'] / (df['segment_duration'] / 3600)

            # set last_vessel_segment
            df['last_vessel_segment'] = 0
            df['last_vessel_segment'].iloc[-1] = 1

            # check if segment ends in a port (only for segment with average_speed < maximal_speed_to_check_if_in_port or with type 'DEFAULT_AIS')
            def get_port(x):
                if ((x.average_speed < maximal_speed_to_check_if_in_port) | (x.type == 'DEFAULT_AIS')):

                    query = 'SELECT id,ST_Distance(ST_POINT(' + str(x.end_longitude) + ',' + str(
                        x.end_latitude) + ', 4326)::geography, geometry_point::geography) from dim_port where ST_Within(ST_POINT(' + str(
                        x.end_longitude) + ',' + str(
                        x.end_latitude) + ', 4326),geometry_buffer) = true AND ST_Distance(ST_POINT(' + str(
                        x.end_longitude) + ',' + str(
                        x.end_latitude) + ', 4326)::geography, geometry_point::geography) <' + str(
                        threshold_distance_to_port)
                    with db.session() as session:
                        res = pd.read_sql(query, engine)  # temporaire
                        session.commit()
                    res.sort_values('st_distance', inplace=True)
                    if res.shape[0] > 0:
                        return res['id'].iloc[0]
                    else:
                        return np.NaN
                else:
                    return np.NaN
                session.close()

            df['port'] = df.apply(get_port, axis=1)

            # get or create new excursion
            # logic : 
            # if segment ends in a port while ongoing excursion is open, then we close the excursion
            # else, if the ongoing excursion is open, then we use the ongoing excursion_id for the segment
            # else, we create a new excursion whose id will become the ongoing excursion_id for this segment and the future ones
            # additionnaly, when we create a new excursion, if the vessel is 'new' then we create an 'empty' excursion
            # else, if the first segment of this new excursion is of type 'DEFAULT_AIS', we estimate the time of departure based
            # on its ending position, distance traveled and a given average exit speed
            df['excursion_id'] = np.NaN
            for a in df.index:
                if (df['port'].iloc[a] >= 0):
                    if (open_ongoing_excursion):
                        close_excursion(ongoing_excursion_id, df['port'].iloc[a], df['end_latitude'].iloc[a],
                                        df['end_longitude'].iloc[a],
                                        df['timestamp_end'].iloc[a])  # put the close excursion function here
                        df['excursion_id'].iloc[a] = ongoing_excursion_id
                        open_ongoing_excursion = False
                else:
                    if (open_ongoing_excursion):
                        df['excursion_id'].iloc[a] = ongoing_excursion_id
                    else:
                        if (is_new_vessel):
                            ongoing_excursion_id = add_excursion(vessel_id, df['timestamp_end'].iloc[a],
                                                                 Point(df['end_longitude'].iloc[a],
                                                                       df['end_latitude'].iloc[
                                                                           a]))  # put the create new excursion function here
                            # ongoing_excursion_id = 1 + mmsi*a # temp excursion id generation
                            is_new_vessel = False
                        else:
                            def get_time_of_departure():
                                if (df['type'].iloc[a] == 'DEFAULT_AIS'):
                                    return df['timestamp_end'].iloc[a] - timedelta(0, 3600 * df['distance'].iloc[
                                        a] / average_exit_speed)
                                else:
                                    return df['timestamp_start'].iloc[a]

                            ongoing_excursion_id = add_excursion(vessel_id,
                                                                 get_time_of_departure())  # put the create new excursion function here
                            # ongoing_excursion_id = mmsi*a # temp excursion id generation
                        open_ongoing_excursion = True
                        df['excursion_id'].iloc[a] = ongoing_excursion_id
        # concat the result for current vessel in the result dataframe
        if (df.shape[0] > 0):
            result = pd.concat([result, df[df['excursion_id'] >= 0]], axis=0)

            # Step 11 : Insertion du résultat dans la database fct_segment
    result.reset_index(drop=True, inplace=True)
    new_segments = []
    for i in result.index:
        new_segment = Segment(
            excursion_id=result['excursion_id'].iloc[i],
            timestamp_start=result['timestamp_start'].iloc[i],
            timestamp_end=result['timestamp_end'].iloc[i],
            segment_duration=result['segment_duration'].iloc[i],
            start_position=Point(result['start_longitude'].iloc[i], result['start_latitude'].iloc[i]),
            end_position=Point(result['end_latitude'].iloc[i], result['end_longitude'].iloc[i]),
            distance=result['distance'].iloc[i],
            average_speed=result['average_speed'].iloc[i],
            speed_at_start=result['speed_at_start'].iloc[i],
            speed_at_end=result['speed_at_end'].iloc[i],
            heading_at_start=result['heading_at_start'].iloc[i],
            heading_at_end=result['heading_at_end'].iloc[i],
            type=result['type'].iloc[i],
            last_vessel_segment=result['last_vessel_segment'].iloc[i]
        )
        new_segments.append(new_segment)

    with db.session() as session:
        new_segments_sql = segment_repository.batch_create_segment(session, new_segments)
        session.commit()

    # Step 12 : Update des excursions modifiées
    # wip
    # for id in result['excursion_id'].unique():
    # update_excursion(id)

    return batch


if __name__ == "__main__":
    logger.info("DEBUT - Création / mise à jour des excursions et des segments")
    run(args.batch_time)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Création / mise à jour des excursions et des segments en {duration:.2f}s")
