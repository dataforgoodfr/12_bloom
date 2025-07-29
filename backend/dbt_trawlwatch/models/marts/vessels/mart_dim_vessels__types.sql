-- mart_dim_vessels__types.sql
/* This file is used to create a mart table for vessel types for API routes:
    - api/v1/vessels/types : Return fishing vessel types

    Fields:
    - type: Fishing vessel "type" (FAO gear subcategory or category)
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels__types',
    tags=['mart', 'dim', 'vessel', 'vessel_type'],
    indexes=[
        {"columns": ["type"], "type": "btree", "unique": true}
    ]
) }}

select
    distinct dim_vessel_details->>'ship_type' as type
from {{ ref("stg_dim_vessels") }} as stg_vessels
where dim_vessel_details->>'ship_type' is not null
order by type asc