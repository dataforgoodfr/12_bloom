-- itm_vessel_first_and_last_positions.sql

{{ config(
    alias = 'itm_vessel_first_and_last_positions',
    schema = 'itm',
    materialized = 'table',
    unique_key = ['vessel_id'],
) }}



select 
    vessel_id, 
    min(position_timestamp) as first_position_timestamp,
    min(position_id) as first_position_id,
    max(position_timestamp) as last_position_timestamp,
    max(position_id) as last_position_id
from {{ ref('stg_vessel_positions') }}
group by vessel_id
order by vessel_id