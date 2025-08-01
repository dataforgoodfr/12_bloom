-- mart_dim_zones__categories.sql
/*
This file is used to create a mart table for zones categories for API routes :
    - api/v1/zones/categories : Return all zones categories

    Fields:
    - category: Protection category of the zone (e.g., 'amp', 'Fishing coastal waters (6-12 NM)')
    - sub_category: Protection sub-category of the zone
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_zones__categories',
    tags=['mart', 'dim', 'zone', 'category'],
    indexes=[
        {"columns": ["category"], "type": "btree"},
        {"columns": ["sub_category"], "type": "btree"},
    ]
) }}

with

itm_zones as (
    select * from {{ ref('stg_dim_zones') }}
)

select
    distinct 
    zone_category as category,
    zone_sub_category as sub_category
from {{ ref('stg_dim_zones') }}
order by category, sub_category
