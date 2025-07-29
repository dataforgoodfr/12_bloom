-- mart_dim_vessels__classes.sql
/* This file is used to create a mart table for vessel size classes for API routes:
    - api/v1/vessels/classes : Return fishing vessel size classes
    Fields:
    - length_class: Fishing vessel "class" (size category)
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels__classes',
    tags=['mart', 'dim', 'vessel', 'class'],
    indexes=[
        {"columns": ["length_class"], "type": "btree", "unique": true}
    ]
) }}

select
    distinct dim_vessel_details->>'length_class' as length_class
from {{ ref("stg_dim_vessels") }} as stg_vessels
where dim_vessel_details->>'length_class' is not null
order by length_class asc