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
    lookback = 3,
    unique_key = ['position_id','zone_id'],
    tags=['itm', 'vessel', 'positions', 'zones'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['position_id', 'zone_id'], 'type': 'btree', 'unique': true},
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
    position
  from {{ ref('itm_vessel_positions') }} {{ MMSI_filter }}
),


its_list as ( -- Liste des correspondances excursions x zones (seulement)
  select 
    excursion_id,
    vessel_id,
    zone_id as zone_id_candidate,
    excursion_start_position_timestamp,
    excursion_end_position_timestamp,
    excursion_position_ids
  from {{ ref('itm_zones_x_excursions_list') }}
),


positions_with_zones_candidates as ( -- Jointure des positions des navires avec la liste des zones concernées par les excursions (préfiltre des zones à analyser en croisement spatial)
  select 
    p.position_id,
    p.vessel_id,
    position_timestamp,
    position,
    zone_id_candidate, -- Récupération des zones candidates pour le croisement spatial
    excursion_id,
    excursion_start_position_timestamp
  from positions p
	join its_list l 
		on p.vessel_id = l.vessel_id 
    and p.position_timestamp between l.excursion_start_position_timestamp and l.excursion_end_position_timestamp
    and p.position_id = ANY(l.excursion_position_ids)
) ,

positions_x_zones as ( -- Positions des navires dans les zones maritimes (croisement spatial)
  select distinct
    p.vessel_id,
    p.excursion_id,
    p.position_id,
    p.position_timestamp,
    z.zone_id,
    z.zone_category,
    z.zone_sub_category,
    p.excursion_start_position_timestamp,
    p.position
  from positions_with_zones_candidates p 
  join (select * from {{ ref('itm_dim_zones') }} ) z
	on true 
    and  z.zone_id = p.zone_id_candidate
    and ST_Contains(z.zone_geometry, p.position)
	order by excursion_id, position_timestamp
)


select * from positions_x_zones
