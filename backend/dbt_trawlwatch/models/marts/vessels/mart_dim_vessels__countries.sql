-- mart_dim_vessels__countries.sql
/* This file is used to create a mart table for vessel countries for API routes:
    - api/v1/vessels/countries : Return fishing vessel countries
    Fields:
    - country_iso3: Fishing vessel "country" (ISO3 code)
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels__countries',
    tags=['mart', 'dim', 'vessel', 'country'],
    indexes=[
        {"columns": ["country_iso3"], "type": "btree", "unique": true}
    ]
) }}

select
    distinct dim_vessel_flag as country_iso3 
from {{ ref("stg_dim_vessels") }} as stg_vessels
where dim_vessel_flag is not null
order by dim_vessel_flag asc