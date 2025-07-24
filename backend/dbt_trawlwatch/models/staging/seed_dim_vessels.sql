-- seed_dim_vessels.sql
-- This file is used to create a staging table for Vessels.
{{ config(
    schema='staging',
    materialized='view',
    tags=['seed','dim', 'vessels']
) 
}}

select 
    md5(concat_ws('|', country_iso3, imo, mmsi ,ship_name )) as vessel_id, -- Création d'un identifiant unique pour le navire
    mmsi,
    ship_name,
    width,
    length,
    length_class,
    country_iso3,
    type as ship_type,
    imo,
    cfr,
    external_marking,
    ircs,
    tracking_activated,
    tracking_status,
    "check" as checked,
    details,
    now() as created_at,
    now() as updated_at
from {{ ref('updated_vessels_table') }} 
where tracking_activated = true
order by mmsi