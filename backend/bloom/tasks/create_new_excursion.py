from bloom.domain.excursion import Excursion
from bloom.container import UseCases
from sqlalchemy.orm import Session
from shapely.geometry import Point
from datetime import datetime,timedelta
from typing import Optional
import pandas as pd
from geoalchemy2.shape import to_shape

def add_excursion(vessel_id: int, departure_at: datetime, departure_position: Optional[Point] = None) -> int:
    use_cases = UseCases()
    db = use_cases.db()
    excursion_repository = use_cases.excursion_repository()
    
    with db.session() as session:
        result = excursion_repository.get_param_from_last_excursion(session, vessel_id)

        if result:
            arrival_port_id = result["arrival_port_id"]
            arrival_position = to_shape(result["arrival_position"])
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
            excursion_duration=None,
            total_time_at_sea=None,
            total_time_in_amp=None,
            total_time_in_territorial_waters=None,
            total_time_in_costal_waters=None,
            total_time_fishing=None,
            total_time_fishing_in_amp=None,
            total_time_fishing_in_territorial_waters=None,
            total_time_fishing_in_costal_waters=None,
            total_time_extincting_amp=None
        )

        new_excursion_sql = excursion_repository.map_to_sql(new_excursion)
        session.add(new_excursion_sql)
        session.commit()
        session.refresh(new_excursion_sql)
    return new_excursion_sql.id

def close_excursion(id: int, port_id: int, latitude: float, longitude: float, arrived_at: datetime) -> None:
    
    use_cases = UseCases()
    db = use_cases.db()
    excursion_repository = use_cases.excursion_repository()

    with db.session() as session:
        excursion = excursion_repository.get_excursion_by_id(session, id)
        
        if excursion:
            excursion.arrival_port_id = port_id
            excursion.arrival_at = arrived_at
            excursion.arrival_position = Point(longitude,latitude)

            close_excursion_sql = excursion_repository.map_to_sql(excursion)
            session.merge(close_excursion_sql)  # Utiliser merge pour mettre à jour l'entité dans la session
            session.commit()
        else:
            raise ValueError(f"No excursion found with ID {id}")

def update_excursion(id :int) -> None :
        
    use_cases = UseCases()
    db = use_cases.db()
    excursion_repository = use_cases.excursion_repository()
    segment_repository = use_cases.segment_repository()

    with db.session() as session:
    
        total_segments = segment_repository.get_segments_by_excursions(session, id)
        
        total_segments['segment_duration'] = pd.to_timedelta(total_segments['segment_duration'])
        excursion_duration=total_segments['segment_duration'].sum()

        in_amp=total_segments[total_segments.loc[:, 'in_amp_zone'] == 1]
        amp_duration=in_amp['segment_duration'].sum()

        in_territorial_waters=total_segments[total_segments.loc[:, 'in_territorial_waters'] == 1]
        territorial_duration=in_territorial_waters['segment_duration'].sum()

        in_costal_waters=total_segments[total_segments.loc[:, 'in_costal_waters'] == 1]
        costal_duration=in_costal_waters['segment_duration'].sum()

        excursion = excursion_repository.get_excursion_by_id(session, id)
        
        if excursion:
            excursion.excursion_duration = excursion_duration
            excursion.total_time_in_amp = amp_duration
            excursion.total_time_in_territorial_waters = territorial_duration
            excursion.total_time_in_costal_waters = costal_duration
            excursion.total_time_at_sea = excursion_duration - territorial_duration - costal_duration
            
            excursion_update_sql = excursion_repository.map_to_sql(excursion)
            session.merge(excursion_update_sql)  # Utiliser merge pour mettre à jour l'entité dans la session
            session.commit()
            session.close()
        else:
            raise ValueError(f"No excursion found with ID {id}")