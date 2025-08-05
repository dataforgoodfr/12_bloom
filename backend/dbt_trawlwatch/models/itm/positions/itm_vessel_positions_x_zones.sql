-- itm_vessel_positions_x_zones.sql
/*
    Liste des positions des navires situées dans les zones maritimes.
*/

{{ config(
    schema='itm',
    materialized='incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-01-01',
    unique_key = ['position_id','excursion_id','zone_id'],
    tags=['itm', 'vessel', 'positions', 'zones'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['position_id', 'zone_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'}
    ]
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}

{% if mmsi_list | length > 0 %}
  {% set MMSI_filter = "where position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
  {% set MMSI_filter = "" %}
{% endif %}

with 

positions as (
  select 
    position_id,
    vessel_id,
    position_timestamp,
    position_point
  from {{ ref('itm_vessel_positions') }} {{ MMSI_filter }}
),

zec_list as ( -- Liste des correspondances excursions x zones (seulement)
  select 
    excursion_id,
    vessel_id,
    zone_id as zone_id_candidate,
    excursion_start_position_timestamp,
    excursion_end_position_timestamp,
    excursion_position_ids
  from {{ ref('itm_zones_x_excursions_list') }}
),

positions_with_zones_candidates as ( -- Jointure des positions des navires avec la liste des zones_x_excursions (préfiltre des zones à analyser en croisement spatial)
  select 
    pos.position_id,
    pos.vessel_id,
    pos.position_timestamp,
    pos.position_point,
    zec.zone_id_candidate, -- Récupération des zones candidates pour le croisement spatial
    zec.excursion_id,
    zec.excursion_start_position_timestamp
  from positions as pos
	inner join zec_list as zec
		on pos.vessel_id = zec.vessel_id
    and pos.position_timestamp between zec.excursion_start_position_timestamp and zec.excursion_end_position_timestamp
    and pos.position_id = any(zec.excursion_position_ids)
) ,

positions_x_zones as ( -- Positions des navires dans les zones maritimes (croisement spatial)
  select distinct
    candidates.vessel_id,
    candidates.excursion_id,
    candidates.position_id,
    candidates.position_timestamp,
    zones.zone_id,
    zones.zone_category,
    zones.zone_sub_category,
    candidates.excursion_start_position_timestamp,
    candidates.position_point
  from positions_with_zones_candidates as candidates
  inner join (select * from {{ ref('stg_dim_zones') }} ) as zones
	  on true 
    and candidates.zone_id_candidate = zones.zone_id
    and st_contains(zones.zone_geometry, candidates.position_point)
	order by candidates.excursion_id, candidates.position_timestamp
)

select * from positions_x_zones
