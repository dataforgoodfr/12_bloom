-- stg_compiled_dim_zones.sql
-- This file is used to create a staging table for enabled zones.   
{{ config(
    schema='staging',
    materialized='view',
    tags=['staging', 'dim', 'zone']
) }}

select 
    id as zone_id,
    name as zone_name,
    category as zone_category,
    sub_category as zone_sub_category,
    json_data as zone_json_data,
    created_at as zone_created_at,
    updated_at as zone_updated_at,
    enable as zone_enable,
    centroid as zone_centroid,
    geometry as zone_geometry
from {{ source('zones','dim_zone') }} 
where enable = true