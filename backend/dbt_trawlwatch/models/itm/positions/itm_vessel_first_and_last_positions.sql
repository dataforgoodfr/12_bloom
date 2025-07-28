-- itm_vessel_first_and_last_positions.sql

{{ config(
    alias = 'itm_vessel_first_and_last_positions',
    schema = 'itm',
    materialized = 'table',
    unique_key = ['vessel_id'],
) }}

with 
vessels as (
    select distinct vessel_id
    from {{ ref('stg_dim_vessels') }}
)

select 
    vessels.vessel_id, 
    min(pos.position_timestamp) as first_position_timestamp,
    min(pos.position_id) as first_position_id,
    max(pos.position_timestamp) as last_position_timestamp,
    max(pos.position_id) as last_position_id
from vessels 
left join {{ ref('stg_vessel_positions') }} as pos
    on vessels.vessel_id = pos.vessel_id
group by vessels.vessel_id
order by vessels.vessel_id
