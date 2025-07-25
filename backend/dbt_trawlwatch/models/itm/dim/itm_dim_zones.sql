-- stg_dim_zones.sql
-- This file is used to create a staging table for enabled zones.   
{{ config(
    schema='itm',
    materialized='table',
    tags=['staging', 'dim', 'zone'],
    indexes= [
        {"columns": ["zone_category"], "type": "btree"},
        {"columns": ["zone_sub_category"], "type": "btree"},
        {"columns": ["zone_id"], "type": "btree", "unique": true},
        {"columns": ["zone_name"], "type": "btree"},
        {"columns": ["zone_enable"], "type": "btree"},
        {"columns": ["zone_created_at", "zone_updated_at"], "type": "btree"},
        {"columns": ["zone_geometry"], "type": "gist"},
        {"columns": ["zone_geometry_metric"], "type": "gist"},
        {"columns": ["zone_geometry_simplified_metric"], "type": "gist"}
    ]
) }}

select 
    *,
    st_transform(zone_geometry, 3857) as zone_geometry_metric,
    ST_simplify(st_transform(zone_geometry, 3857),25) as zone_geometry_simplified_metric
    
from {{ ref('stg_dim_zones') }} 
order by zone_category, zone_sub_category, zone_id