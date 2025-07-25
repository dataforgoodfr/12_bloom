-- itm_vessel_last_raw_position.sql

/*
    Retourne la liste des dernières positions RAW des navires (source directe spire_ais_data) pour chaque navire.
    Vessel_id est associé par jointure avec itm_dim_vessels sur le MMSI + sa période de validité
    matchant le position_timestamp de la dernière position   

*/


with 

dim_vessels as (
    select 
        vessel_id,
        dim_mmsi_mmsi,
        dim_mmsi_start_date,
        dim_mmsi_end_date
    from {{ ref('stg_dim_mmsi') }}
),

last_vessel_raw_positions as (
    select 
        
        vessel_id,
        max(created_at) as position_ais_created_at__raw_max,
        last(position_id order by created_at, position_id) as position_id__raw_last,
        last(position_mmsi order by created_at, position_id) as position_mmsi__raw_last,
        last(position_timestamp order by created_at, position_id) as position_timestamp__raw_last,
        last(position_latitude order by created_at, position_id) as position_latitude__raw_last,
        last(position_longitude order by created_at, position_id) as position_longitude__raw_last,
        last(position_speed order by created_at, position_id) as position_speed__raw_last,
        last(position_heading order by created_at, position_id) as position_heading__raw_last,
        last(position_course order by created_at, position_id) as position_course__raw_last,
        last(position_rot order by created_at, position_id) as position_rot__raw_last

        from dim_vessels
        left join {{ source('spire','spire_ais_data') }} spire on dim_vessels.dim_mmsi_mmsi = spire.position_mmsi
        and utils.safe_between(spire.position_timestamp, dim_vessels.dim_mmsi_start_date, dim_vessels.dim_mmsi_end_date)
        where spire.position_timestamp is not null
        group by vessel_id
)

select 
        vessel_id,
        position_id__raw_last,
        position_timestamp__raw_last,
        position_mmsi__raw_last,
        position_latitude__raw_last,
        position_longitude__raw_last,
        position_speed__raw_last,
        position_heading__raw_last,
        position_course__raw_last,
        position_rot__raw_last,
        position_ais_created_at__raw_max,
        to_char(position_timestamp__raw_last, 'YYYYMM') as position_ais_created_at__raw_max_month,
        date_trunc('day', position_ais_created_at__raw_max) as position_ais_created_at__raw_max_day,

        ST_MakePoint(position_longitude__raw_last, position_latitude__raw_last, 4326) as position,
        'Last_AIS_position'::varchar as position_status

from last_vessel_raw_positions
