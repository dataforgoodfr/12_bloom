import warnings
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Optional

import numpy as np
import pandas as pd
from geoalchemy2.shape import to_shape
from geopy import distance
from shapely.geometry import Point
from sqlalchemy.orm import Session

from bloom.container import UseCases
from bloom.domain.excursion import Excursion
from bloom.domain.segment import Segment
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.logger import logger
from bloom.domain.rel_segment_zone import RelSegmentZone
from bloom.infra.repositories.repository_rel_segment_zone import RelSegmentZoneRepository
from bloom.infra.repositories.repository_port import PortRepository
from bloom.domain.metrics import Metrics #1

warnings.filterwarnings("ignore")

# minimal distance to consider a vessel being in a port (in meters)
threshold_distance_to_port = 5000
# maximal average speed of a vessel to check if it's in a port (in knot)
maximal_speed_to_check_if_in_port = 0.1
# average speed to take when vessel exit a port (in knot/h)
average_exit_speed = 7


def to_coords(row: pd.Series) -> pd.Series:
    if pd.isna(row["end_position"]) is False:
        row["longitude"] = row["end_position"].x
        row["latitude"] = row["end_position"].y

    return row


def add_excursion(session: Session, vessel_id: int, departure_at: datetime,
                  departure_position: Optional[Point] = None) -> int:
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    port_repository = use_cases.port_repository()

    result = excursion_repository.get_param_from_last_excursion(session, vessel_id)

    if result:
        arrival_port_id = result["arrival_port_id"]
        arrival_position = to_shape(result["arrival_position"]) if result["arrival_position"] else None
    else:
        arrival_port_id = None
        arrival_position = None

    new_excursion = Excursion(
        vessel_id=vessel_id,
        departure_port_id=arrival_port_id if departure_position is None else None,
        departure_at=departure_at,
        departure_position=arrival_position if departure_position is None else departure_position,
        arrival_port_id=None,
        arrival_at=None,
        arrival_position=None,
        excursion_duration=timedelta(0),
        total_time_at_sea=timedelta(0),
        total_time_in_amp=timedelta(0),
        total_time_in_territorial_waters=timedelta(0),
        total_time_in_zones_with_no_fishing_rights=timedelta(0),
        total_time_fishing=timedelta(0),
        total_time_fishing_in_amp=timedelta(0),
        total_time_fishing_in_territorial_waters=timedelta(0),
        total_time_fishing_in_zones_with_no_fishing_rights=timedelta(0),
        total_time_default_ais=timedelta(0)
    )
    new_excursion = excursion_repository.create_excursion(session, new_excursion)

    if departure_position is None :
        port_repository.update_port_has_excursion(session, arrival_port_id)

    return new_excursion.id


def close_excursion(session: Session, excursion_id: int, port_id: int, latitude: float, longitude: float,
                    arrived_at: datetime) -> None:
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    port_repository = use_cases.port_repository()

    excursion = excursion_repository.get_excursion_by_id(session, excursion_id)

    if excursion:
        excursion.arrival_port_id = port_id
        excursion.arrival_at = arrived_at
        excursion.arrival_position = Point(longitude, latitude)
        excursion_repository.update_excursion(session, excursion)
        port_repository.update_port_has_excursion(session, port_id)


def run():
    use_cases = UseCases()
    db = use_cases.db()
    segment_repository = use_cases.segment_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    port_repository = use_cases.port_repository()
    excursion_repository = use_cases.excursion_repository()
    metrics_repository = use_cases.metrics_repository() #1
    nb_created_excursion = 0
    nb_closed_excursion = 0

    process_start = datetime.now(timezone.utc)
    point_in_time = None
    position_count = None
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "create_update_excursions_segments",
        )
        logger.info(f"Lecture des nouvelles positions depuis le {point_in_time}")
        batch = vessel_position_repository.get_positions_with_vessel_created_updated_after(session, point_in_time)
        position_count=len(batch)
        logger.info(f"{position_count} nouvelles positions")
        last_segment = segment_repository.get_last_vessel_id_segments(session)
        last_segment["longitude"] = None
        last_segment["latitude"] = None
        last_segment = last_segment.apply(to_coords, axis=1)

        logger.info("Création des excursions")
        result = pd.DataFrame()
        for vessel_id in batch["vessel_id"].unique():
            df_end = batch.loc[batch["vessel_id"] == vessel_id].copy()
            df_end.rename(columns={"timestamp": "timestamp_end",
                            "heading": "heading_at_end",
                            "speed": "speed_at_end",
                            "longitude": "end_longitude",
                            "latitude": "end_latitude"
                            }, inplace=True)
            df_end.sort_values("timestamp_end", inplace=True)
            df_end.reset_index(drop=True, inplace=True)
            # get every end entry but the last one ; each one of them will be the start point of a segment
            if len(df_end)>1:
                df_start = df_end.iloc[0:-1, :].copy()
                for col in df_start.columns:
                    df_start.rename(columns={col: col.replace("end", "start")}, inplace=True)
                vessel_last_segment = pd.DataFrame()
                if last_segment.shape[0] > 0:
                    vessel_last_segment = last_segment.loc[
                        last_segment["vessel_id"] == vessel_id, ["mmsi", "timestamp_end", "heading_at_end", "speed_at_end",
                                                                    "end_position", "excursion_id", "arrival_port_id"]]
                    vessel_last_segment["start_latitude"] = vessel_last_segment["end_position"].apply(lambda x: x.y)
                    vessel_last_segment["start_longitude"] = vessel_last_segment["end_position"].apply(lambda x: x.x)
                    vessel_last_segment.drop("end_position", inplace=True, axis=1)
                    vessel_last_segment.rename(columns={"timestamp_end": "timestamp_start",
                                                        "heading_at_end": "heading_at_start",
                                                        "speed_at_end": "speed_at_start",
                                                        }, inplace=True)
                if vessel_last_segment.shape[0] > 0:
                    # if there's a last segment for this vessel, then it's not the first time a position for this vessel is received
                    is_new_vessel = False
                    # and it becomes the start point of the first new segment
                    df_start.loc[-1] = vessel_last_segment.iloc[0]
                    df_start.sort_index(inplace=True)
                    df_start.reset_index(drop=True, inplace=True)
                    # checks if the excursion of the last segment is closed or not
                    if vessel_last_segment["arrival_port_id"].iloc[0] >= 0:
                        open_ongoing_excursion = False
                    else:
                        open_ongoing_excursion = True
                        ongoing_excursion_id = int(vessel_last_segment["excursion_id"].iloc[0])

                else:
                    # if there's no last segment for this vessel, then it's the first time a position for this vessel is received
                    is_new_vessel = True
                    # so we duplicate the starting point to have the first segment while setting it up 1s behind in time (so timestamp_start != timestamp_end)
                    df_start.loc[-1] = df_start.loc[0]
                    df_start["timestamp_start"].iloc[-1] += timedelta(0, -1)
                    df_start.sort_index(inplace=True)
                    df_start.reset_index(drop=True, inplace=True)
                    open_ongoing_excursion = False
                # concat start and end point together
                df = pd.concat([df_start, df_end], axis=1)
                # removing segment with same timestamp_start and timestamp_end (no update)
                df = df[df["timestamp_start"] != df["timestamp_end"]].copy()
                # reseting index
                df.reset_index(inplace=True, drop=True)
                if (df.shape[0] > 0):
                    # calculate distance
                    def get_distance_in_nautical_miles(x) -> float:
                        p1 = (x.start_latitude, x.start_longitude)
                        p2 = (x.end_latitude, x.end_longitude)
                        return distance.distance(p1, p2).nautical

                    df["distance"] = df.apply(get_distance_in_nautical_miles, axis=1)
            else:
                #df_start=df_end.copy()
                vessel_last_segment = pd.DataFrame()
                if last_segment.shape[0] > 0:
                    vessel_last_segment = last_segment.loc[
                        last_segment["vessel_id"] == vessel_id, ["mmsi", "timestamp_end", "heading_at_end", "speed_at_end",
                                                                    "end_position", "excursion_id", "arrival_port_id"]]
                    vessel_last_segment["start_latitude"] = vessel_last_segment["end_position"].apply(lambda x: x.y)
                    vessel_last_segment["start_longitude"] = vessel_last_segment["end_position"].apply(lambda x: x.x)
                    vessel_last_segment.drop("end_position", inplace=True, axis=1)
                    vessel_last_segment.rename(columns={"timestamp_end": "timestamp_start",
                                                        "heading_at_end": "heading_at_start",
                                                        "speed_at_end": "speed_at_start",
                                                        }, inplace=True)
                if vessel_last_segment.shape[0] > 0:
                    # if there's a last segment for this vessel, then it's not the first time a position for this vessel is received
                    is_new_vessel = False
                    df_start= vessel_last_segment
                    df_start.reset_index(drop=True, inplace=True)
                    # checks if the excursion of the last segment is closed or not
                    if vessel_last_segment["arrival_port_id"].iloc[0] >= 0:
                        open_ongoing_excursion = False
                    else:
                        open_ongoing_excursion = True
                        ongoing_excursion_id = int(vessel_last_segment["excursion_id"].iloc[0])

                else:
                    # if there's no last segment for this vessel, then it's the first time a position for this vessel is received
                    is_new_vessel = True
                    # so we duplicate the starting point to have the first segment while setting it up 1s behind in time (so timestamp_start != timestamp_end)
                    df_start = df_end.copy()
                    for col in df_start.columns:
                        df_start.rename(columns={col: col.replace("end", "start")}, inplace=True)                    
                    df_start["timestamp_start"] += timedelta(0, -1)
                    df_start.sort_index(inplace=True)
                    df_start.reset_index(drop=True, inplace=True)
                    open_ongoing_excursion = False
                # concat start and end point together
                df = pd.concat([df_start, df_end], axis=1)
                # removing segment with same timestamp_start and timestamp_end (no update)
                df = df[df["timestamp_start"] != df["timestamp_end"]].copy()
                # reseting index
                df.reset_index(inplace=True, drop=True)

            if (df.shape[0] > 0):
                # calculate distance
                def get_distance_in_nautical_miles(x) -> float:
                    p1 = (x.start_latitude, x.start_longitude)
                    p2 = (x.end_latitude, x.end_longitude)
                    return distance.distance(p1, p2).nautical

                df["distance"] = df.apply(get_distance_in_nautical_miles, axis=1)

                # calculate duration in seconds
                def get_duration(x) -> float:
                    return (x.timestamp_end - x.timestamp_start).total_seconds()

                df["segment_duration"] = df.apply(get_duration, axis=1)

                # set default type as AT_SEA
                df["type"] = "AT_SEA"

                # set type as default_ais for segment with duration > 35 min
                df.loc[df["segment_duration"] >= 2100, "type"] = "DEFAULT_AIS"

                # calculate average speed in knot
                df["average_speed"] = df["distance"] / (df["segment_duration"] / 3600)

                # set last_vessel_segment
                df["last_vessel_segment"] = 0
                if len(df) >1 :
                    df["last_vessel_segment"].iloc[-1] = 1
                else : 
                    df["last_vessel_segment"] = 1

                # check if segment ends in a port (only for segment with average_speed < maximal_speed_to_check_if_in_port or with type 'DEFAULT_AIS')
            def get_port(x, session):
                if x.type == 'DEFAULT_AIS' or x.average_speed < maximal_speed_to_check_if_in_port:
                    res = port_repository.get_closest_port_in_range(session, x.end_longitude, x.end_latitude,
                                                                    threshold_distance_to_port)
                    if res:
                        (port_id, distance) = res
                        return port_id
                    else:
                        return None
                else:
                    return None
            df["port"] = df.apply(get_port, axis=1, args=(session,))

            # get or create new excursion
            # logic :
            # if segment ends in a port while ongoing excursion is open, then we close the excursion
            # else, if the ongoing excursion is open, then we use the ongoing excursion_id for the segment
            # else, we create a new excursion whose id will become the ongoing excursion_id for this segment and the future ones
            # additionnaly, when we create a new excursion, if the vessel is 'new' then we create an 'empty' excursion
            # else, if the first segment of this new excursion is of type 'DEFAULT_AIS', we estimate the time of departure based
            # on its ending position, distance traveled and a given average exit speed
            df["excursion_id"] = np.NaN
            for a in df.index:
                if df["port"].iloc[a] is not None and df["port"].iloc[a] >= 0:
                    if (open_ongoing_excursion):
                        close_excursion(session, ongoing_excursion_id, int(df["port"].iloc[a]),
                                        df["end_latitude"].iloc[a],
                                        df["end_longitude"].iloc[a],
                                        df["timestamp_end"].iloc[a])  # put the close excursion function here
                        df["excursion_id"].iloc[a] = ongoing_excursion_id
                        open_ongoing_excursion = False
                        nb_closed_excursion += 1
                elif open_ongoing_excursion:
                    df["excursion_id"].iloc[a] = ongoing_excursion_id
                else:
                    if is_new_vessel:
                        ongoing_excursion_id = add_excursion(session, int(vessel_id),
                                                                df["timestamp_end"].iloc[a],
                                                                Point(df["end_longitude"].iloc[a],
                                                                    df["end_latitude"].iloc[
                                                                        a]))
                        is_new_vessel = False
                        nb_created_excursion += 1
                    else:
                        def get_time_of_departure():
                            if (df['type'].iloc[a] == 'DEFAULT_AIS'):
                                return df['timestamp_end'].iloc[a] - timedelta(0, 3600 * df['distance'].iloc[
                                    a] / average_exit_speed)
                            else:
                                return df["timestamp_start"].iloc[a]

                        ongoing_excursion_id = add_excursion(session, int(vessel_id),
                                                                get_time_of_departure())  # put the create new excursion function here
                        nb_created_excursion += 1
                    open_ongoing_excursion = True
                    df["excursion_id"].iloc[a] = ongoing_excursion_id
            # concat the result for current vessel in the result dataframe
            if (df.shape[0] > 0):
                result = pd.concat([result, df[df["excursion_id"] >= 0]], axis=0)
        logger.info(f"{nb_created_excursion} excursion(s) créées")
        logger.info(f"{nb_closed_excursion} excursion(s) cloturés")
        logger.info("Création des segments")
        result.reset_index(drop=True, inplace=True)
        new_segments = []
        for i in result.index:
            new_segment = Segment(
                excursion_id=result["excursion_id"].iloc[i],
                timestamp_start=result["timestamp_start"].iloc[i],
                timestamp_end=result["timestamp_end"].iloc[i],
                segment_duration=result["segment_duration"].iloc[i],
                start_position=Point(result["start_longitude"].iloc[i], result["start_latitude"].iloc[i]),
                end_position=Point(result["end_longitude"].iloc[i], result["end_latitude"].iloc[i]),
                distance=result["distance"].iloc[i],
                average_speed=result["average_speed"].iloc[i],
                speed_at_start=result["speed_at_start"].iloc[i],
                speed_at_end=result["speed_at_end"].iloc[i],
                heading_at_start=result["heading_at_start"].iloc[i],
                heading_at_end=result["heading_at_end"].iloc[i],
                type=result["type"].iloc[i],
                last_vessel_segment=result["last_vessel_segment"].iloc[i],
                in_zone_with_no_fishing_rights=False,
                in_amp_zone=False,
                in_territorial_waters=False
            )
            new_segments.append(new_segment)
        segment_repository.batch_create_segment(session, new_segments)
        logger.info(f"{len(new_segments)} segment(s) créés")

        # On vide un peu la mémoire
        session.flush()
        new_segments = None
        df = None

        # Recherche des zones et calcul / mise à jour des stats
        logger.info("Mise en relation des segments avec les zones et calcul des statistiques d'excursion")
        result = segment_repository.find_segments_in_zones_created_updated_after(session, point_in_time)
        new_rels = []
        excursions = {}
        segments = []
        new_metricss=[]
        max_created_updated = point_in_time
        i=0
        for segment, zones in result.items():
            segment_in_zone = False
            vessel_attributes= segment_repository.get_vessel_attribute_by_segment_created_updated_after(session, segment.id, point_in_time)#metrics_repository.get_vessel_excursion_segment_by_id(session,segment.id) #1
            types='AT_SEA'
            zones_names=[]
            for zone in zones:
                if segment.type == "DEFAULT_AIS":
                    # Issue 234: ne pas créer les relations pour les segments en default AIS
                    types='DEFAULT_AIS'
                    continue
                segment_in_zone = True
                new_rels.append(RelSegmentZone(segment_id=segment.id, zone_id=zone.id))
                if zone.category == "amp":
                    segment.in_amp_zone = True
                    types='in_amp'
                elif zone.category == "Fishing coastal waters (6-12 NM)":
                    country_iso3 = vessel_attributes.country_iso3
                    beneficiaries = zone.json_data.get("beneficiaries", [])
                    if country_iso3 not in beneficiaries:
                        segment.in_zone_with_no_fishing_rights = True
                        types='in_zone_with_no_fishing_rights'
                elif zone.category == "Clipped territorial seas":
                    country_iso3 = vessel_attributes.country_iso3
                    if country_iso3 != "FRA":
                        segment.in_zone_with_no_fishing_rights = True
                        types='in_zone_with_no_fishing_rights'
                elif zone.category == "Territorial seas":
                    segment.in_territorial_waters = True
                    types="in_territorial_water" #1
                #elif zone.category == "white zone":    #prospectif
                #    segment.in_white_zone = True
                #    types="white_zone"  
                #duration_total_seconds = segment.segment_duration.total_seconds()

                new_metrics= Metrics(#1
                    timestamp = segment.timestamp_start, 
                    vessel_id = vessel_attributes.id,
                    vessel_mmsi = vessel_attributes.mmsi,
                    ship_name = vessel_attributes.ship_name,
                    vessel_country_iso3=vessel_attributes.country_iso3,
                    vessel_imo=vessel_attributes.imo,
                    type = types, 
                    duration_total = segment.segment_duration,
                    duration_fishing = segment.segment_duration if segment.type == 'FISHING' else None,
                    zone_id=zone.id,
                    zone_category=zone.category,
                    zone_name = zone.name,
                    zone_sub_category=zone.sub_category
                ) 

                new_metricss.append(new_metrics) 

            if segment_in_zone:
                segments.append(segment)

            # Mise à jour de l'excursion avec le temps passé dans chaque type de zone
            excursion = excursions.get(segment.excursion_id,
                                       excursion_repository.get_excursion_by_id(session, segment.excursion_id))
            if segment.in_amp_zone:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_amp += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_amp += segment.segment_duration
            if segment.in_zone_with_no_fishing_rights:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_zones_with_no_fishing_rights += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_zones_with_no_fishing_rights += segment.segment_duration
            if segment.in_territorial_waters:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_territorial_waters += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_territorial_waters += segment.segment_duration

            excursion.excursion_duration += segment.segment_duration
            if segment.type == "FISHING":
                excursion.total_time_fishing += segment.segment_duration
            elif segment.type == "DEFAULT_AIS":
                if excursion.total_time_default_ais is None:
                    excursion.total_time_default_ais = timedelta(0)
                excursion.total_time_default_ais += segment.segment_duration

            excursion.total_time_at_sea = excursion.excursion_duration - (
                    excursion.total_time_in_zones_with_no_fishing_rights + excursion.total_time_in_territorial_waters)

            excursions[excursion.id] = excursion

            
            # Détection de la borne supérieure du traitement
            if segment.updated_at and segment.updated_at > max_created_updated:
                max_created_updated = segment.updated_at
            elif segment.created_at > max_created_updated:
                max_created_updated = segment.created_at

        
        excursion_repository.batch_update_excursion(session, excursions.values())
        logger.info(f"{len(excursions.values())} excursions mises à jour")
        segment_repository.batch_update_segment(session, segments)
        logger.info(f"{len(segments)} segments mis à jour")
        RelSegmentZoneRepository.batch_create_rel_segment_zone(session, new_rels)
        logger.info(f"{len(new_rels)} associations(s) créées")
        metrics_repository.batch_create_metrics(session, new_metricss) #1
        logger.info(f"{len(new_metricss)} metrics(s) créés") #1
        vessels_ids = set(exc.vessel_id for exc in excursions.values())
        nb_last = segment_repository.update_last_segments(session, vessels_ids)
        logger.info(f"{nb_last} derniers segments mis à jour")
        now = datetime.now(timezone.utc)
        TaskExecutionRepository.set_point_in_time(session, "create_update_excursions_segments", now)
        session.commit()
        if point_in_time:
            TaskExecutionRepository.set_duration(session,
                                                 "create_update_excursions_segments",
                                                 now,
                                                 datetime.now(timezone.utc)-process_start)
        if now != None:
            TaskExecutionRepository.set_position_count(session,
                                             "create_update_excursions_segments",
                                             now,
                                             position_count)
        session.commit()


if __name__ == "__main__":
    logger.info("DEBUT - Création / mise à jour des excursions et des segments")
    time_start = perf_counter()
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Création / mise à jour des excursions et des segments en {duration:.2f}s")
