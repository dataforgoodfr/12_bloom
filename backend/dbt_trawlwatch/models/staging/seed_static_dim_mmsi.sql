-- seed_static_dim_mmsi.sql
-- This file is used to create a staging table for MMSI - vessel_id links.

/*
    Extraction des couples distincts MMSI - vessel_id à partir de la table des navires statiques.
    Passage au format de pattern schema de seed_historical_dim_mmsi.
*/

{{ config(
    schema='staging',
    materialized='view',
    tags=['seed','dim', 'mmsi','static']
) 
}}


select distinct
    id as vessel_id, -- Création d'un identifiant unique vessel_id, à partir du CFR ou de l'IMO, ou si aucun n'est dispo, ...
    mmsi as dim_mmsi_mmsi,
    cast(NULL as TIMESTAMPTZ) as dim_mmsi_start_date, -- Date de début de validité du MMSI -> NULL
    cast(NULL as TIMESTAMPTZ) as dim_mmsi_end_date, -- Date de fin de validité du MMSI -> NULL
    cast('STATIC' as VARCHAR) as dim_mmsi_origin, -- Origine des données du MMSI STATIC | HISTORIZED
    NULL as dim_mmsi_details,
    now() as dim_mmsi_created_at -- Méta: date de création de la dimension dans la base de données

from  {{ ref('static_vessels_table') }} 
where tracking_activated = TRUE
order by vessel_id