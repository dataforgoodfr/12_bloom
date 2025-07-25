-- seed_dim_vessels.sql
-- This file is used to create a staging table for Vessels.
{{ config(
    enabled=true,
    schema='staging',
    materialized='view',
    tags=['seed','dim', 'vessels','historical'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['dim_vessel_name'], 'type': 'btree'},
        {'columns': ['dim_vessel_flag'], 'type': 'btree'},
        {'columns': ['dim_vessel_imo'], 'type': 'btree'},
        {'columns': ['dim_vessel_cfr'], 'type': 'btree'},
        {'columns': ['dim_vessel_call_sign'], 'type': 'btree'},
        {'columns': ['dim_vessel_external_marking'], 'type': 'btree'},
        {'columns': ['dim_vessel_loa'], 'type': 'btree'}
    ]
) 
}}

select 
    id as vessel_id,
    ship_name as dim_vessel_name,
    loa	country_iso3 as dim_vessel_flag	
    imo as dim_vessel_imo,
    NULL::varchar as dim_vessel_cfr,
    ircs as dim_vessel_call_sign,
    external_marking as dim_vessel_external_marking,
    length as dim_vessel_loa,
    


    start_date as dim_vessel_start_date,
    end_date as dim_vessel_end_date,

    TRUE as tracking_activated,
    status as dim_vessel_status,
    source as dim_vessel_source,
    'HISTORICAL'::varchar as dim_vessel_origin

    jsonb_build_object(
        'gear', gear,
        'ship_type', type,
        'main_engine_power', main_engine_power,
        'auxiliary_engine_power', auxiliary_engine_power,
        'tonnage_gt' as tonnage_gt,
        'other_tonnage' as other_tonnage,
        'fish_hold_volume' as fish_hold_volume,
        'carrying_capacity' as carrying_capacity
    ) as dim_vessel_details,

    now() as dim_vessel_created_at
from {{ ref('historical_vessels_table') }} as historical_vessels  -- A adapter quand la table de référence changera
order by vessel