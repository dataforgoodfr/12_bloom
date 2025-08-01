-- observ_vessel_positions_max_upd.sql
/*
    Load only the maximum update timestamp_position from the stg_vessel_positions table.
*/

{{ config(
        schema='observ',
        enabled=true,
        materialized='view',
        tags=['observ', 'vessel', 'positions', 'max_update']
) }}


select 
    --max(position_ais_created_at_max) as max_position_ais_created_at,
    max(position_stg_created_at) as max_position_stg_created_at
from {{ ref('stg_vessel_positions') }}
