-- mart_metrics__vessels_at_sea.sql
/*
This file is used to create a mart table for number of vessels at sea for API routes :
    - api/v1/metrics/vessels-at-sea : Return the number of vessels at sea between dates

    Fields:
    - day_date: Day of the count
    - vessel_ids: List of vessel IDs that were at sea on that day
    - count_vessels_at_sea: Number of vessels at sea on that day
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__vessels_at_sea',
    tags=['mart', 'metrics', 'vessel'],
    indexes=[
        {"columns": ["day_date"], "type": "btree", "unique": true}
    ]
) }}

select 
    daysegments_date as day_date,
    array_agg(distinct vessel_id) as vessel_ids,
    count(distinct vessel_id) as count_vessels_at_sea,
    now() as created_at
from {{ ref('itm_vessel_segments_by_date') }}
group by daysegments_date
order by daysegments_date