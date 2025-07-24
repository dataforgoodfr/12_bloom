-- seed_dim_ports.sql
-- This file is used to create a staging table for ports.
{{ config(
    schema='staging',
    materialized='view',
    alias='seed_dim_ports',
    tags=['staging', 'dim', 'port'],
    indexes=[
        {"columns": ["port_id"], "type": "btree", "unique": true},
        {"columns": ["port_locode"], "type": "btree", "unique": true},
        {"columns": ["port_name"], "type": "btree"},
        {"columns": ["port_geometry_point"], "type": "gist"}
    ]
) }}

with

raw_ports as ( -- Chargement des données brutes des ports
    select * from {{ ref('ports') }}
),

countries as ( -- Normalisation des codes pays en ISO3
    select 
        "ISO3166-1-Alpha-2" as country_iso2,
        "ISO3166-1-Alpha-3" as country_iso3
    from {{ ref('country_codes') }}
),

enhanced_ports as ( -- Amélioration des données des ports (Id, géométrie, métadonnées))
    select 
        p.locode as port_id, -- Création d'un identifiant unique pour le port à partir de locode
        p.port as port_name,
        c.country_iso3 as port_country_iso3,
        p.locode as port_locode,
        p.latitude as port_latitude,
        p.longitude as port_longitude,
        p.url as port_url,
        null::boolean as port_has_excursion,
        p.geometry_point::geometry(Point, 4326) AS port_geometry_point,
        now() as port_created_at,
        now() as port_updated_at
    from raw_ports p
    left join countries c on left( p.locode::text, 2 ) = c.country_iso2
)

select * from enhanced_ports