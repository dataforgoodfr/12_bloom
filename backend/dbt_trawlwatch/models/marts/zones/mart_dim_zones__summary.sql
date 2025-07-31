-- mart_dim_zones__summary.sql
/*
This file is used to create a mart table for zones summarised for API routes :
    - api/v1/zones/summary : Return summarised zones 

    Fields:
    - id: Unique identifier of the zone
    - category: Protection category of the zone (e.g., 'amp', 'Fishing coastal waters (6-12 NM)')
    - sub_category: Protection sub-category of the zone
    - name: Name of the zone
    - created_at: Creation timestamp of the zone
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_zones__summary',
    tags=['mart', 'dim', 'zone'],
    indexes=[
        {"columns": ["id"], "type": "btree", "unique": true},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["category"], "type": "btree"},
        {"columns": ["sub_category"], "type": "btree"},
        {"columns": ["created_at"], "type": "btree"}
    ]
) }}

with

itm_zones as (
    select * from {{ ref('stg_dim_zones') }}
)

select
    zone_id as id,
    zone_category as category,
    zone_sub_category as sub_category,
    zone_name as name,
    zone_created_at as created_at
from {{ ref('stg_dim_zones') }}
order by zone_id
