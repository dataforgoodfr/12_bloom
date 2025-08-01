-- mart_metrics__vessels_in_mpas.sql
/*
This file is used to create a mart table for number of vessels in MPAs for API routes :
    - api/v1/metrics/vessels-in-activity : Return the number of vessels in MPAs between dates

    Fields:
    - day_date: Day of the count
    - vessel_ids: List of vessel IDs that were in MPAs on that day
    - count_vessels_in_mpas: Number of vessels in MPAs on that day
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__vessels_in_mpas',
    tags=['mart', 'metrics', 'vessel'],
    indexes=[
        {"columns": ["day_date"], "type": "btree", "unique": true}
    ]
) }}

select 
    daysegments_date as day_date,
    array_agg(distinct vessel_id) as vessel_ids,
    count(distinct vessel_id) as count_vessels_in_mpas,
    now() as created_at
from {{ ref('itm_vessel_segments_by_date') }}
where time_in_amp_zone > '00:00:00' -- Est sensé marcher mais problème dans itm_vessel_segments_by_date : il n'y a pas de ligne où time_in_amp_zone > '00:00:00'
group by daysegments_date
order by daysegments_date
