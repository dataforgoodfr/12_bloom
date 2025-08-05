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
    {% if is_incremental() %}
        case
            when this.first_position_timestamp is null then min(pos.position_timestamp)
            when min(pos.position_timestamp) < this.first_position_timestamp then min(pos.position_timestamp)
            else this.first_position_timestamp 
        end as first_position_timestamp,
        case 
            when this.first_position_id is null then min(pos.position_id)
            when min(pos.position_id) is null then this.first_position_id
            when min(pos.position_id) < this.first_position_id then min(pos.position_id)
            else this.first_position_id 
        end as first_position_id,
    {% else %}
    min(pos.position_timestamp) as first_position_timestamp,
    min(pos.position_id) as first_position_id,
    {% endif %}

    max(pos.position_timestamp) as last_position_timestamp,
    max(pos.position_id) as last_position_id,
    now() as position_first_and_last_created_at
from vessels 

left join (select * from {{ ref('stg_vessel_positions') }} ) as pos
    on vessels.vessel_id = pos.vessel_id

{% if is_incremental() %}
 inner join {{ this }} as this
    on vessels.vessel_id = this.vessel_id 
    and pos.position_stg_created_at > this.position_first_and_last_created_at - interval '1 hour'
    and pos.position_timestamp not between this.first_position_timestamp and this.last_position_timestamp
{% endif %}

{% if is_incremental() %}
group by vessels.vessel_id, this.first_position_timestamp, this.first_position_id
{% else %}
group by vessels.vessel_id
{% endif %}

order by vessels.vessel_id
