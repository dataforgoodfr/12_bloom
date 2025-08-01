-- mart_dim_vessels__excursions_by_date.sql
/*
This file is used to create a mart table for excursions for API routes :
    - api/v1/vessels/{vessel_id}/excursions : Return paginated detailed excursions by id between two dates

    Fields:
    - excursion_id: Unique identifier of the excursion
    - day_excursion_date: Day of the excursion
    - vessel_id: Identifier of the vessel associated with the excursion
    - departure_port_id: Identifier of the port from which the vessel departed
    - arrival_port_id: Identifier of the port where the vessel arrived
    - departure_on: Departure date of the excursion
    - arrival_on: Arrival date of the excursion
    - departure_at: Departure timestamp of the excursion
    - arrival_at: Arrival timestamp of the excursion
    - (arrival_position: Position of the vessel upon arrival) => removed
    - (departure_position: Position of the vessel upon departure) => removed
    - total_time_at_sea: Total time spent at sea during the day
    - total_time_in_amp: Total time spent in marine protected areas (AMP) during the day
    - total_time_in_territorial_waters: Total time spent in territorial waters during the day
    - total_time_in_zones_with_no_fishing_rights: Total time spent in zones with no fishing rights during the day
    - total_time_fishing: Total time spent fishing during the day
    - total_time_fishing_in_amp: Total time spent fishing in marine protected areas (AMP) during the day
    - total_time_fishing_in_territorial_waters: Total time spent fishing in territorial waters during the day
    - total_time_fishing_in_zones_with_no_fishing_rights: Total time spent fishing in zones with no fishing rights during the day
    - total_time_default_ais: Total time the vessel was not broadcasting its AIS signal during the day
    - excursion_created_at: Creation timestamp of the excursion record 
    - created_at: Creation timestamp of the record 
*/


{{
    config(
        schema='marts',
        materialized='table',
        alias='mart_dim_vessels__excursions_by_date',
        tags=['mart', 'dim', 'vessel', 'excursion'],
        indexes=[
            {"columns": ["excursion_id"], "type": "btree"},
            {"columns": ["vessel_id"], "type": "btree"},
            {"columns": ["day_excursion_date"], "type": "brin"},
        ]
    )
}}

select 
    itm_segments_day.excursion_id,
    itm_segments_day.vessel_id,
    max(itm_excursions.excursion_start_position_timestamp) as departure_at,
    max(itm_excursions.excursion_end_position_timestamp) as arrival_at,
    max(itm_excursions.excursion_start_position_timestamp_day) as departure_on,
    max(itm_excursions.excursion_end_position_timestamp_day) as arrival_on,
    max(itm_excursions.excursion_port_departure) as departure_port_id,
    max(itm_excursions.excursion_port_arrival) as arrival_port_id,
    itm_segments_day.daysegments_date as day_excursion_date,
    sum(itm_segments_day.segment_duration) as total_time_at_sea,

    -- Additionner les temps passés dans les zones AMP en excluant les segments DEFAULT_AIS
    sum(case when itm_segments_day.segment_type = 'DEFAULT_AIS' then NULL else itm_segments_day.time_in_amp_zone end) as total_time_in_amp, 
    -- Additionner les temps passés en défaut d'AIS
    sum(case when itm_segments_day.segment_type = 'DEFAULT_AIS' then itm_segments_day.segment_duration end) as total_time_default_ais, 
    
    sum(itm_segments_day.time_in_territorial_waters) as total_time_in_territorial_waters,
    sum(itm_segments_day.time_in_zone_with_no_fishing_rights) as total_time_in_zones_with_no_fishing_rights,
    NULL as total_time_fishing,
    NULL as total_time_fishing_in_amp,
    NULL as total_time_fishing_in_territorial_waters,
    NULL as total_time_fishing_in_zones_with_no_fishing_rights,
    max(itm_excursions.excursion_created_at) as excursion_created_at,
    now() as created_at
from {{ ref('itm_vessel_segments_by_date') }} as itm_segments_day
left join {{ ref('itm_vessel_excursions') }} as itm_excursions
on itm_segments_day.excursion_id = itm_excursions.excursion_id
group by itm_segments_day.excursion_id, itm_segments_day.vessel_id, itm_segments_day.daysegments_date
order by itm_segments_day.vessel_id asc, day_excursion_date asc
