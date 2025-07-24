-- itm_vessel_positions_x_zones.sql
/*
    Liste des positions des navires situées dans les zones maritimes.
*/

{{ config(
    enabled = false,
    schema='itm',
    materialized='incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_ais_created_at',
    batch_size = 'day',
    begin = '2024-01-01',
    lookback = 3,
    unique_key = ['position_id'],
    tags=['itm', 'vessel', 'positions', 'zones'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'}
    ]
) }}



with 

positions as (
  select 
    position_id,
    vessel_id,
    position_timestamp,
    position,
    position_ais_created_at
  from {{ ref('itm_vessel_positions') }} p
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
