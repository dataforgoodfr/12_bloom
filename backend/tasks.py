from invoke import Collection,task,Context,call
from datetime import datetime,timezone, timedelta
from math import floor,ceil
import time
from dateutil import parser
import multiprocessing as mp
import signal
import os
import isodate

from bloom.logger import logger


from bloom.container import UseCases
import pandas as pd
import numpy as np
from geopy import distance
from bloom.domain.vessel_position import VesselPosition
from shapely.geometry import Point

namespace=Collection()

etl=Collection("etl")

def schedule_next(start_date:datetime,schedule_interval:timedelta,now=None):
    nb_interval=(now-start_date)/schedule_interval
    next=start_date+(ceil(nb_interval))*schedule_interval
    return next

@task
def test(ctx):
    logger.info("test invoke")

@task()
def task_extract_ais_data_from_spire_api_table_spire_ais_data(ctx:Context,interval_start:datetime,interval_end:datetime):
    logger.info(f"{os.getpid()} extract_ais_data_from_spire_api interval_start={interval_start}-{interval_end} STARTED")
    if datetime.now(timezone.utc) - ctx['schedule_interval'] >= interval_start \
        and datetime.now(timezone.utc) - ctx['schedule_interval'] <= interval_end:
        logger.info("Executing API CALL")
    else:
        logger.info("interval ")
    logger.info(f"{os.getpid()} extract_ais_data_from_spire_api interval_start={interval_start}-{interval_end} FINISHED")



def to_coords(row: pd.Series) -> pd.Series:
    if pd.isna(row["end_position"]) is False:
        row["longitude"] = row["end_position"].x
        row["latitude"] = row["end_position"].y

    return row


# distance.distance takes pair of (lat, lon) tuples:
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
        speed=row["speed"],
    )

@task(help={"batch": "size"})
def task_transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions(ctx,interval_start:datetime,interval_end:datetime,batch:int=7):
 
    logger.info(f"{os.getpid()} transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions interval_start={interval_start}-{interval_end} STARTED")
    
    
    use_cases = UseCases()
    db = use_cases.db()
    spire_repository = use_cases.spire_ais_data_repository()
    excursion_repository = use_cases.excursion_repository()
    segment_repository = use_cases.segment_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    with db.session() as session:
        # Step 1: load SPIRE batch: read from SpireAisData
        logger.info(f"Lecture des nouvelles positions de Spire en base")
        batch = spire_repository.get_all_data_between_date(session, interval_start, interval_end)
        logger.info(f"Traitement des positions entre le {interval_start} et le {interval_end}")
        logger.info(f"{len(batch)} nouvelles positions de Spire")
        batch.dropna(
            subset=[
                "position_latitude",
                "position_longitude",
                "position_timestamp",
                "position_update_timestamp",
            ],
            inplace=True,
        )
        # Step 2: load excursion from fct_excursion where date_arrival IS NULL
        excursions = excursion_repository.get_current_excursions(session)
        
        # Step 3: load last_segment where last_vessel_segment == 1
        last_segment = segment_repository.get_last_vessel_id_segments(session)
        last_segment["longitude"] = None
        last_segment["latitude"] = None
        last_segment = last_segment.apply(to_coords, axis=1)

        
        # Step 4: merge batch with last_segment on vessel_id.
        # If column _merge == "left_only" --> this is a new vessel (keep it)
        batch = batch.merge(
            last_segment,
            how="left",
            on="vessel_id",
            suffixes=["", "_segment"],
            indicator=True,
        )
        batch.rename(columns={"_merge": "new_vessel"}, inplace=True)
        batch["new_vessel"] = batch["new_vessel"] == "left_only"

        # Step 5: merge batch with excursions
        # If column _merge == "left_only" --> the excursion is closed
        batch = batch.merge(
            excursions,
            how="left",
            on="vessel_id",
            suffixes=["", "_excursion"],
            indicator=True,
        )
        batch.rename(columns={"_merge": "excursion_closed"}, inplace=True)
        batch["excursion_closed"] = batch["excursion_closed"] == "left_only"
        

        # Step 6: compute speed between last and current position
        # Step 6.1. Compute distance in km between last and current position
        batch["distance_since_last_position"] = batch.apply(
            lambda row: get_distance(
                (row["position_latitude"], row["position_longitude"]),
                (row["latitude"], row["longitude"]),
            ),
            axis=1,
        )

        # Step 6.2. Compute time in hours between last and current position
        ## If timestamp_end is NULL --> new_vessel is TRUE (record will be kept)
        ## --> fillna with anything to avoid exception
        batch.loc[batch["timestamp_end"].isna(), "timestamp_end"] = batch.loc[
            batch["timestamp_end"].isna(), "position_timestamp"
        ].copy()
        batch["timestamp_end"] = pd.to_datetime(batch["timestamp_end"], utc=True)
        batch["position_timestamp"] = pd.to_datetime(batch["position_timestamp"], utc=True)
        batch["time_since_last_position"] = (
                batch["position_timestamp"] - batch["timestamp_end"]
        )
        batch["hours_since_last_position"] = (
                batch["time_since_last_position"].dt.seconds / 3600
        )

        # Step 6.3. Compute speed: speed = distance / time
        batch["speed"] = (
                batch["distance_since_last_position"] / batch["hours_since_last_position"]
        )
        batch["speed"] *= 0.5399568  # Conversion km/h to
        batch["speed"] = batch["speed"].fillna(batch["position_speed"])
        batch.replace([np.nan], [None], inplace=True)
        # Step 7: apply to_keep flag: keep only positions WHERE:
        # - row["new_vessel"] is True, i.e. there is a new vessel_id
        # - OR speed is not close to 0, i.e. vessel moved significantly since last position
        batch["to_keep"] = (batch["new_vessel"] == True) | ~(  # detect new vessels
                (batch["excursion_closed"] == True)  # if last excursion closed
                & (batch["speed"] <= 0.01)  # and speed < 0.01: don't keep
        )

        # Step 8: filter unflagged rows to insert to DB
        batch = batch.loc[batch["to_keep"] == True].copy()

        # Step 9: insert to DataBase
        clean_positions = batch.apply(map_vessel_position_to_domain, axis=1).values.tolist()
        vessel_position_repository.batch_create_vessel_position(session, clean_positions)
        logger.info(f"Ecriture de {len(clean_positions)} positions dans la table vessel_positions")
        session.commit()

    logger.info(f"{os.getpid()} transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions interval_start={interval_start}-{interval_end} FINISHED")


@task()
def task_api_etl(ctx,interval_start:datetime,interval_end:datetime):
    task_extract_ais_data_from_spire_api_table_spire_ais_data(ctx,interval_start,interval_end)
    task_transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions(ctx,interval_start,interval_end)


@task()
def pipeline_main(ctx:Context,
                  start_date:str="2024-06-01 00:00:00+00:00",
                  schedule_interval:str="PT15M",
                  backfill:bool=False):
    start_date=parser.parse(start_date)
    schedule_interval=isodate.parse_duration(schedule_interval)
    ctx["start_date"]=start_date
    ctx["schedule_interval"]=schedule_interval
    ctx["backfill"]=backfill
    
    logger.info(f"start_date:{start_date}")
    logger.info(f"schedule_interval {schedule_interval}")
    logger.info(f"backfill {backfill}")

    list_process=[]

    now=start_date
    while(True):
        if(backfill):
            now=now+schedule_interval
        else:
            now=datetime.now(timezone.utc)
        next=schedule_next(start_date=start_date,
                           schedule_interval=schedule_interval,
                           now=now)
        logger.info(f"Waiting for next execution slot {next}")
        while(now<next):
            time.sleep(1)
        for proc in list_process:
            if proc.is_alive():
                logger.info("Previous tasks not finished")
                logger.info("Scheduling Error: process is still alive. Terminating...")
                proc.terminate()
                time.sleep(0.1)
                print(f"Exit Code: {proc.exitcode}")
                if(proc.exitcode == -signal.SIGTERM):
                    #TODO send mail
                    pass
                list_process.remove(proc)

        process_api_etl=mp.Process(target=task_api_etl,
                            args=[ctx,next-schedule_interval,next],)
        list_process.append(process_api_etl)
        process_api_etl.start()
        if backfill:
            process_api_etl.join()
        #task_extract_ais_data_from_spire_api_table_spire_ais_data(ctx,)
        #task_transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions(ctx,start_date=start_date,end_date=start_date+schedule_interval)

namespace.add_task(task_extract_ais_data_from_spire_api_table_spire_ais_data)
namespace.add_task(task_transform_and_load_ais_data_from_table_spire_ais_data_to_vessel_positions)
namespace.add_task(pipeline_main)