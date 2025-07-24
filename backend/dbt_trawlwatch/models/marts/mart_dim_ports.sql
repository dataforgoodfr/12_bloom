-- mart_dim_ports.sql
-- This file is used to create a mart table for ports.
{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_ports',
    tags=['mart', 'dim', 'port'],
    indexes=[
        {"columns": ["id"], "type": "btree", "unique": true},
        {"columns": ["locode"], "type": "btree", "unique": true},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["geometry_point"], "type": "gist"},
        {"columns": ["has_excursion"], "type": "btree"}
    ]
) }}

with

itm_ports as (
    select * from {{ ref('itm_dim_ports') }}
)

select
    port_id as id,
    port_name as name,
    port_locode as locode,
    port_url as url,
    port_country_iso3 as country_iso3,
    port_latitude as latitude,
    port_longitude as longitude,
    port_geometry_point as geometry_point,
    port_has_excursion as has_excursion,
    port_created_at as created_at,
    port_updated_at as updated_at
from {{ ref("itm_dim_ports") }}