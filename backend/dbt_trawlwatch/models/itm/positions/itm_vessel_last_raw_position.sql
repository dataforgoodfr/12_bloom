-- itm_vessel_last_raw_position.sql
/*
    Retourne la liste des dernières positions RAW des navires (source directe spire_ais_data) pour chaque navire.
    Vessel_id est associé par jointure avec itm_dim_vessels sur le MMSI + l'IMO (pour tenir compte des réaffectations de MMSI).
*/

{{ config(
    schema = 'itm',
    materialized = 'table',
    unique_key = ['vessel_id'],
    indexes = [
        {'columns': ['vessel_id'], 'type': 'btree', 'unique': True},
        {'columns': ['position_timestamp__raw_last'], 'type': 'btree'},
        {'columns': ['position_ais_created_at__raw_max'], 'type': 'btree'}
    ]
) }}


with 

dim_mmsi as (
    select 
        vessel_id,
        dim_mmsi_mmsi,
        dim_mmsi_start_date,
        dim_mmsi_end_date
    from {{ ref('stg_dim_mmsi') }}
),

dim_vessels as (
    select 
        vessel_id,
        dim_vessel_imo
    from {{ ref('stg_dim_vessels') }}
),

dim_vessels_mmsi as (
    select 
        dv.vessel_id,
        dm.dim_mmsi_mmsi,
        dv.dim_vessel_imo
    from dim_vessels as dv
    left join dim_mmsi as dm 
        on dv.vessel_id = dm.vessel_id
),

last_vessel_raw_positions as (
    select *
    from (
        select 
            dim_vessels_mmsi.vessel_id,
            spire.id as spire_id__raw_last,
            spire.vessel_mmsi as position_mmsi__raw_last,
            spire.position_timestamp as position_timestamp__raw_last,
            spire.position_latitude as position_latitude__raw_last,
            spire.position_longitude as position_longitude__raw_last,
            spire.position_speed as position_speed__raw_last,
            spire.position_heading as position_heading__raw_last,
            spire.position_course as position_course__raw_last,
            spire.position_rot as position_rot__raw_last,
            spire.created_at as position_ais_created_at__raw_max,
            row_number() over (
                partition by dim_vessels_mmsi.vessel_id
                order by spire.created_at desc, spire.position_timestamp desc
            ) as rn
        from dim_vessels_mmsi
        left join {{ source('spire','spire_ais_data') }} as spire
            on dim_vessels_mmsi.dim_mmsi_mmsi = spire.vessel_mmsi
            and dim_vessels_mmsi.dim_vessel_imo = cast(spire.vessel_imo as varchar) --and dim_vessels_mmsi.dim_vessel_imo != 'NA'
    ) as t
    where (rn is NULL or rn = 1)
)

select 
    vessel_id,
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
    st_setsrid(st_makepoint(position_longitude__raw_last, position_latitude__raw_last), 4326) as position_point__raw_last,
    cast('Last_AIS_position' as varchar) as position_status,
    now() as last_raw_position_evaluated_at
from last_vessel_raw_positions
