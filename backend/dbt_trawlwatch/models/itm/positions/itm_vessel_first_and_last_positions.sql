-- itm_vessel_first_and_last_positions.sql

{{ config(
    alias = 'itm_vessel_first_and_last_positions',
    schema = 'itm',
    materialized = 'incremental',
    incremental_strategy = 'merge',
    tags = ['itm', 'vessels', 'positions','first','last'],
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
    max(pos.position_id) as last_position_id,
    now() as position_first_and_last_created_at
from vessels 

left join {{ ref('stg_vessel_positions') }} as pos
    on vessels.vessel_id = pos.vessel_id

{% if is_incremental() %}
 inner join {{ this }} as this
    on vessels.vessel_id = this.vessel_id 
    and pos.position_stg_created_at > this.position_first_and_last_created_at - interval '1 hour'
    and pos.position_timestamp not between this.first_position_timestamp and this.last_position_timestamp
{% endif %}

group by vessels.vessel_id
order by vessels.vessel_id
