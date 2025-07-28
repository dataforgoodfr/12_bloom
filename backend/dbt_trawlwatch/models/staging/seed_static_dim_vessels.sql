-- seed_dim_vessels.sql
-- This file is used to create a staging table for Vessels.

/*
    Ce modèle fait converger 3

*/
{{ config(
    schema='staging',
    materialized='view',
    tags=['seed','dim', 'vessels','static'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['dim_vessel_name'], 'type': 'btree'},
        {'columns': ['dim_vessel_flag'], 'type': 'btree'},
        {'columns': ['dim_vessel_imo'], 'type': 'btree'},
        {'columns': ['dim_vessel_cfr'], 'type': 'btree'},
        {'columns': ['dim_vessel_call_sign'], 'type': 'btree'},
        {'columns': ['dim_vessel_external_marking'], 'type': 'btree'},
        {'columns': ['dim_vessel_loa'], 'type': 'btree'}
    ]
) 
}}

select 
    id as vessel_id, -- Création d'un identifiant unique pour le navire
    ship_name as dim_vessel_name,
    country_iso3 as dim_vessel_flag,
    imo as dim_vessel_imo,
    cfr as dim_vessel_cfr,
    ircs as dim_vessel_call_sign,
    external_marking as dim_vessel_external_marking,
    length as dim_vessel_loa,
    cast(NULL as TIMESTAMPTZ) as dim_vessel_start_date,
    cast(NULL as TIMESTAMPTZ) as dim_vessel_end_date,
    tracking_activated,
    tracking_status as dim_vessel_status,
    "check" as dim_vessel_source,
    cast('STATIC' as VARCHAR) as dim_vessel_origin, -- Origine des données du navire STATIC | HISTORIZED'

    jsonb_build_object(
        'width', width,
        'length_class', length_class,
        'ship_type', type
    ) as dim_vessel_details, -- Infos de dimension du navire en JSON

    now() as seed_dim_vessel_created_at -- Méta: date de création de la dimension dans la base de données

from {{ ref('static_vessels_table') }} 
where tracking_activated = TRUE
order by vessel_id
