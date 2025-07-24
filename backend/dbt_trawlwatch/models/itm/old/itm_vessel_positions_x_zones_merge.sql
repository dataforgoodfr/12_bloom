-- itm_vessel_positions_x_zones.sql
/*
    Liste des positions des navires dans les zones maritimes.

    ------------- !!!! A refactoriser complètement sous forme de table de lien
*/

{{ config(
    enabled=false,
    schema='itm',
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['vessel_id', 'zone_id', 'excursion_id'],
    tags=['itm', 'vessel', 'positions', 'zones'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'}
    ],
    pre_hook="SET statement_timeout TO '30min';
             SET lock_timeout TO '30min';
             SET idle_in_transaction_session_timeout TO '30min';"
) }}


-- itm_vessel_positions_in_zone.sql
/*
    Liste des positions des navires dans les zones maritimes.
*/


{% set manuel_incremental_start = '2025-07-01 00:00:00'%}
{% set manuel_incremental_gap = '1 month' %}

with 

positions_known_vessels as ( -- Chargement des positions des navires nouvelles correspondant à des navires déjà connus
  select 
    position_id,
    vessel_id,
    position_timestamp,
    position,
    position_ais_created_at
  from {{ ref('itm_vessel_positions') }} p
  {% if is_incremental() %}
    join {{ this }} as already_treated
        on p.vessel_id = already_treated.vessel_id
      and p.position_ais_created_at > already_treated.position_ais_created_at
  {% else %}
   limit 0 -- Lors de la première exécution, voir plus bas pour les positions des navires encore inconnus dans cette table
  {% endif %}
),

positions_unknown_vessels as ( -- Chargement des positions des navires nouvelles correspondant à des navires inconnus par cette table
  select 
    position_id,
    vessel_id,
    position_timestamp,
    position,
    position_ais_created_at
  from {{ ref('stg_vessel_positions') }} p    
  {% if is_incremental() %}
    where not exists (
            select 1 from {{ this }} as already_treated
            where itm_vessel_positions.vessel_id = already_treated.vessel_id
        )
  {% else %}
   where true-- Lors de la première exécution, tous les navires sont inconnus de cette table
  {% endif %}
),

positions as ( -- Union des positions des navires connus et inconnus
  select * from positions_known_vessels
  union all
  select * from positions_unknown_vessels
),

its_list as ( -- Liste des correspondances excursions x zones (seulement)
  select 
    ex.excursion_id,
    ex.vessel_id,
    zone_id as zone_id_candidate,
    ex.excursion_start_position_timestamp,
    ex.excursion_end_position_timestamp,
    ex.excursion_position_ids
  from {{ ref('itm_zones_x_excursions_list') }} ex
),


positions_with_zones_candidates as ( -- Jointure des positions des navires avec la liste des zones concernées par les excursions (préfiltre des zones à analyser en croisement spatial)
  select 
    p.position_id,
    p.vessel_id,
    position_timestamp,
    position,
    zone_id_candidate, -- Récupération des zones candidates pour le croisement spatial
    excursion_id,
    excursion_start_position_timestamp,
    position_ais_created_at
  from positions p
	join its_list l 
		on p.vessel_id = l.vessel_id 
    and p.position_timestamp between l.excursion_start_position_timestamp and l.excursion_end_position_timestamp
    and p.position_id = ANY(l.excursion_position_ids)
) ,

positions_x_zones as ( -- Positions des navires dans les zones maritimes (croisement spatial)
  select 
    p.vessel_id,
    p.excursion_id,
    p.position_id,
    p.position_timestamp,
    p.position_ais_created_at,
    z.zone_id,
    z.zone_category,
    z.zone_sub_category,
    p.position
  from positions_with_zones_candidates p 
  join {{ ref('itm_dim_zones') }} z
	on true 
    and  z.zone_id = p.zone_id_candidate
    and ST_Contains(z.zone_geometry, p.position)
	order by excursion_id, position_timestamp
)


select * from positions_x_zones

{% if is_incremental() %}
where position_ais_created_at > (select max(position_ais_created_at) from {{ this }})
{% endif %}
