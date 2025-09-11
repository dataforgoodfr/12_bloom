-- mart_metrics__mpas_activity.sql
/*
This file is used to create a mart table for number of vessels in MPAs for API routes :
    - /metrics/vessels-count-in-mpas : Return the number of vessels in MPAs between dates
    - /metrics/mpas-visited: Return the number of zones visited between dates

    Fields:
    - day_date: Day of the count
    - vessel_ids: List of vessel IDs that were in MPAs on that day
    - zones_ids: List of MPA zone IDs where vessels were present on that day
    - count_vessels: Number of vessels in MPAs on that day
    - count_zones: Number of unique MPA zones with vessels on that day
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__mpas_activity',
    tags=['mart', 'metrics', 'vessel'],
    indexes=[
        {"columns": ["day_date"], "type": "btree", "unique": true}
    ]
) }}

-- Modifier et passer par itm_vessel_segments pour avoir accès aux zones individuelles

with mpas_data as (
    select
        daysegments_date,
        unnest(zones_crossed) as zone_id
    from {{ ref('itm_vessel_segments_by_date') }}
    left join {{ ref('stg_dim_zones') }} dz on cast(dz.zone_id as text) = any(zones_crossed)
    where zones_crossed is not null and dz.zone_category = 'amp'
)

select 
    seg.daysegments_date as day_date,
    array_agg(distinct seg.vessel_id) as vessel_ids,
    array_agg(distinct mpas.zone_id) as zones_ids,
    count(distinct seg.vessel_id) as count_vessels,
    count(distinct mpas.zone_id) as count_zones,
    now() as created_at
from {{ ref('itm_vessel_segments_by_date') }} as seg
left join mpas_data mpas on seg.daysegments_date = mpas.daysegments_date
where time_in_amp_zone > '00:00:00'
group by seg.daysegments_date
order by seg.daysegments_date desc