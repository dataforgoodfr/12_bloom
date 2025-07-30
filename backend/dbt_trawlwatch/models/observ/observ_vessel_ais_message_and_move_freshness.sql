-- observ_vessel_ais_message_and_move_freshness.sql
/*
    Calculates an interval as now() - the last RAW position from itm_vessel_last_raw_positions for each vessel
    Calculates and interval as now() - the last effective move from itm_vessel_first_and_last_position for each vessel
*/

{{ config(
    schema='observ',
    materialized='table',
    tags=['observ', 'vessel', 'last_mmsi_update'],
    indexes=[
        {"columns": ["vessel_id"], "type": "btree", "unique": True},
        {"columns": ["last_ais_message_freshness"], "type": "btree"},
        {"columns": ["last_effective_move_freshness"], "type": "btree"}
    ]
) }}

with

last_raw_positions as (
    select 
        vessel_id,
        now() - max(position_ais_created_at__raw_max) as last_ais_message_freshness,
        now() - max(position_timestamp__raw_last) as last_position_timestamp_freshness
    from {{ ref('itm_vessel_last_raw_position') }}
    group by vessel_id
),

last_effective_move as (
    select 
        vessel_id,
        now() - last_position_timestamp as last_effective_move_freshness
    from {{ ref('itm_vessel_first_and_last_positions') }}
)

select
    r.vessel_id,
    r.last_ais_message_freshness,
    r.last_position_timestamp_freshness,
    e.last_effective_move_freshness
from last_raw_positions as r
left join last_effective_move as e 
    on r.vessel_id = e.vessel_id
order by r.vessel_id
