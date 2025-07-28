-- itm_zones_x_excursions_list.sql

/*
Recense les occurences d'intersections entre excursions et zones maritimes.
*/

{{ config(
    schema='itm',
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['zone_id', 'excursion_id'],
    tags=['itm', 'zones', 'tracks'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['zone_category'], 'type': 'btree'},
        {'columns': ['zone_sub_category'], 'type': 'btree'},
        {'columns': ['excursion_id','zone_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_end_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp','excursion_end_position_timestamp'], 'type': 'btree'}
    ]
) }}

with

excursions as (
    select
        vessel_id,
        excursion_id,
        excursion_line,
        excursion_position_ids,
        excursion_start_position_timestamp,
        excursion_end_position_timestamp,
        excursion_position_itm_created_at
    from {{ ref('itm_vessel_excursions_details') }} 
    {% if is_incremental() %}
    where excursion_position_itm_created_at >= (select max(excursion_position_itm_created_at) from {{ this }})
    {% endif %}

),

zones as ( -- Chargement des zones maritimes
    select 
        zone_id,
        zone_category,
        zone_sub_category,
        zone_geometry
    from {{ ref('stg_dim_zones') }}
),

pre_excursions_x_zones as ( -- Test de croisement spatial des positions courantes des navires avec les zones maritimes (pas de calcul de l'intersection, trop long)
    select
        exc.vessel_id,
        exc.excursion_id,
        zon.zone_id,
        zon.zone_category,
        zon.zone_sub_category,
        exc.excursion_position_ids,
        exc.excursion_start_position_timestamp,
        exc.excursion_end_position_timestamp,
        exc.excursion_position_itm_created_at
    from excursions as exc
    inner join zones as zon
		on st_intersects(zon.zone_geometry, exc.excursion_line)
)

select * from pre_excursions_x_zones
