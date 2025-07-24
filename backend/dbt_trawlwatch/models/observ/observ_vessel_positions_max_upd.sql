/*
    Load only the maximum update timestamp from the stg_vessel_positions table.
    This model is used to track the latest update time for staged vessel positions data.
*/

{{ config(
        schema='observ',
        enabled=true,
        materialized='table'
) }}


select max(position_ais_created_at_max) as max_position_ais_created_at, max(position_stg_created_at) as max_position_stg_created_at
from {{ ref('stg_vessel_positions') }}