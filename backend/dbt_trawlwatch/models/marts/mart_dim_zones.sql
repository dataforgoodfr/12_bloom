-- mart_dim_zones.sql
/*
This file is used to create a mart table for zones for API routes :
    - api/v1/zone/{zone_id} : Return one zone by id 
    - api/v1/zones: Return paginated zones
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_zones',
    tags=['mart', 'dim', 'zone'],
    indexes=[
        {"columns": ["id"], "type": "btree", "unique": true},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["geometry"], "type": "gist"},
        {"columns": ["category"], "type": "btree"},
        {"columns": ["sub_category"], "type": "btree"},
        {"columns": ["centroid"], "type": "gist"},
        {"columns": ["created_at", "updated_at"], "type": "btree"}
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
    zone_created_at as created_at,
    zone_updated_at as updated_at,
    zone_geometry as geometry,
    st_centroid(zone_geometry) as centroid,
    zone_json_data as json_data,
    zone_enable as enable
from itm_zones
order by zone_id