-- mart_dim_vessels__trackedcount.sql
/* This file is used to create a mart table for vessel currently tracked number for API routes:
    - api/v1/vessels/trackedCount : Return fishing vessel currently tracked number
    Fields:
    - count: Number of tracked fishing vessels at last update.
    - updated_at: Timestamp of when the count was last updated
    Note: This table/route is used to provide a quick count of currently tracked vessels and will in the end be replaced by a more comprehensive solution (e.g. request by timerange).
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels__trackedcount',
    tags=['mart', 'dim', 'vessel', 'metric']  
) }}

with

tracked_vessels as (
    select 
        vessel_id,
        utils.safe_between( date_trunc('day', now())::date,  
                date_trunc('day', dim_vessel_start_date)::date, 
                date_trunc('day', dim_vessel_end_date)::date ) as is_tracked
    from {{ ref("stg_dim_vessels") }} as stg_vessels
)

select 
    count(*) as count,
    now() as updated_at
from tracked_vessels
where is_tracked = true