-- mart_metrics__zones_visited.sql
/*
This file is used to create a mart table for zones visited for API routes :
    - api/v1/metrics/zone-visited : Return list of visited zones with total duration between dates

    Fields:
    - day_date: Day of the count
    - zone_id: Identifier of the zone visited
    - category: Category of the zone (e.g., 'amp', 'Territorial seas', etc.)
    - sub_category: Sub-category of the zone
    - name: Name of the zone
    - zone_created_at: Creation timestamp of the zone record
    - centroid: Geographic centroid of the zone
    - visiting_duration: Total time spent in the zone
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__zones_visited',
    tags=['mart', 'metrics', 'zone'],
    indexes=[
        {"columns": ["day_date"], "type": "btree"},
        {"columns": ["zone_id"], "type": "btree"},
        {"columns": ["category"], "type": "btree"},
        {"columns": ["sub_category"], "type": "btree"},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["centroid"], "type": "gist"}
    ]
) }}

with 

zones_data as (
    select 
        daysegments_date as day_date,
        unnest(zones_crossed) as zone_id,
        segment_duration
    from {{ ref('itm_vessel_segments_by_date') }}
)

select 
    day_date,
    zd.zone_id,
    zones.zone_name as name,
    zones.zone_category as category,
    zones.zone_sub_category as sub_category,
    zones.zone_created_at as zone_created_at,
    zones.zone_centroid as centroid,
    sum(segment_duration) as visiting_duration,
    now() as created_at
from zones_data as zd
left join {{ ref('stg_dim_zones') }} as zones
on zones.zone_id::varchar = zd.zone_id
group by day_date, zd.zone_id, zones.zone_name, zones.zone_category, zones.zone_sub_category, zones.zone_created_at, zones.zone_centroid
order by category, day_date
