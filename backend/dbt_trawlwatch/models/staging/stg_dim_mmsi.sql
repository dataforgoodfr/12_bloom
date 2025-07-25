-- stg_dim_mmsi.sql

/*
    Consolide les 2 tables de liens MMSI - vessel_id :
    - seed_static_dim_mmsi : liens statiques
    - seed_historical_dim_mmsi : liens historisés

    Règle de consolidation :
    - Si le navire a des données historisées, on utilise celles-ci
    - Si le navire n'a pas de données historisées, on utilise les données statiques
*/

{{ config(
    schema='staging',
    materialized='table',
    tags=['staging', 'dim', 'mmsi'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['dim_mmsi_mmsi'], 'type': 'btree'},
        {'columns': ['dim_mmsi_start_date'], 'type': 'btree'},
        {'columns': ['dim_mmsi_end_date'], 'type': 'btree'}
    ]
) 
}}

with

static_mmsi as ( -- MMSI statiques
    select 
    vessel_id, -- Identifiant unique pour vessel_id
    dim_mmsi_mmsi,
    dim_mmsi_start_date, -- Date de début de validité du MMSI -> NULL
    dim_mmsi_start_date, -- Date de fin de validité du MMSI -> NULL
    from {{ ref('seed_static_dim_vessels') }}
),

historical_mmsi as ( -- MMSI historisés
    select 
    vessel_id, -- Identifiant unique pour vessel_id
    dim_mmsi_mmsi,
    dim_mmsi_start_date, -- Date de début de validité du MMSI
    dim_mmsi_end_date, -- Date de fin de validité du MMSI
    from {{ ref('seed_historical_dim_mmsi') }}
),

union_mmsi as ( -- Union des MMSI statiques et historisés
    select * from static_mmsi
    union all
    select * from historical_mmsi
),

flagged_mmsi as (   -- MMSI avec indicateur d'historisation (pour les prioriser dans la consolidation)
    select 
        *,
        bool_or(dim_mmsi_start_date is not null) over (partition by vessel_id) as has_historical,
        

    from union_mmsi
)
select 
    vessel_id,
    dim_mmsi_mmsi,
    dim_mmsi_start_date,
    dim_mmsi_end_date,
    now() as stg_dim_mmsi_created_at -- Date de création de la dimension dans la base de données
from flagged_mmsi
-- Consolidation des liens MMSI - vessel_id avec priorité aux MMSI historisés
where (has_historical and dim_mmsi_start_date is not null)
   or (not has_historical and dim_mmsi_start_date is null);