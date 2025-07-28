-- stg_dim_vessels.sql
-- This models creates an intermediate view for Vessels.
/*
    Consolide les données des navires à partir des 2 sources : 
    - la source statiques servant initialement de table de dimension pour les navires (static_dim_vessels, anciennement updated_dim_vessels)
    - la source historisée qui contient les données de dimension sucessives des navires avec début et fin de validité (itm_vessel_positions)

    Règle de consolidation : 
    - Si le navire a des données historisées, on utilise celles-ci
    - Si le navire n'a pas de données historisées, on utilise les données statiques
    - Si le navire a des données historisées et statiques, on utilise les

*/

{{ config(
    schema='staging',
    materialized='table',
    tags=['staging','dim', 'vessels']
) 
}}

with 

staged_historical_vessels  as ( -- Charger les données de la table de référence des navires historisés
    select
        vessel_id,
        dim_vessel_name,
        dim_vessel_flag,
        dim_vessel_imo,
        dim_vessel_cfr,
        dim_vessel_call_sign,
        dim_vessel_external_marking,
        dim_vessel_loa,
        dim_vessel_start_date,
        dim_vessel_end_date,
        tracking_activated,
        dim_vessel_status,
        dim_vessel_source,
        dim_vessel_origin, -- Origine des données du navire STATIC | HISTORICAL
        dim_vessel_details
    from {{ ref('seed_historical_dim_vessels') }}
),
staged_static_vessels  as ( -- Charger les données de la table de référence des navires statiques
    select 
        vessel_id,
        dim_vessel_name,
        dim_vessel_flag,
        dim_vessel_imo,
        dim_vessel_cfr,
        dim_vessel_call_sign,
        dim_vessel_external_marking,
        dim_vessel_loa,
        dim_vessel_start_date, -- Date de début de validité du navire -> NULL
        dim_vessel_end_date, -- Date de fin de validité du navire -> NULL
        tracking_activated,
        dim_vessel_status,
        dim_vessel_source,
        dim_vessel_origin, -- Origine des données du navire STATIC | HISTORICAL
        dim_vessel_details
    from {{ ref('seed_static_dim_vessels') }}
),
dim_vessels_union as (
    select * from staged_historical_vessels
    union all
    select * from staged_static_vessels
),
flagged as (
  select *,
         bool_or(dim_vessel_origin = 'HISTORICAL') over (partition by vessel_id) as has_historical
  from dim_vessels_union
)
select 
  vessel_id,
  dim_vessel_name,
  dim_vessel_flag,
  dim_vessel_imo,
  dim_vessel_cfr,
  dim_vessel_call_sign,
  dim_vessel_external_marking,
  dim_vessel_loa,
  dim_vessel_start_date,
  dim_vessel_end_date,
  tracking_activated,
  dim_vessel_status,
  dim_vessel_source,
  dim_vessel_origin,
  dim_vessel_details,
  NOW() as stg_dim_vessel_created_at -- Méta: date de création de la dimension dans la base de données
from flagged
where (has_historical and dim_vessel_origin = 'HISTORICAL')
   or (not has_historical and dim_vessel_origin = 'STATIC')