-- itm_vessel_tracks_in_zones.sql
/*
    Croisement entre les excursions et les zones maritimes.
    Méthode 1 : sans distinction des catégories de zones maritimes.
*/

{{ config(
    enabled = false,
    materialized = 'table',
    unique_key = ['zone_id', 'excursion_id'],
    indexes = [
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['zone_id'], 'type': 'btree'},
        {'columns': ['zone_category'], 'type': 'btree'},
        {'columns': ['zone_sub_category'], 'type': 'btree'},
        {'columns': ['track_in_zone'], 'type': 'gist'}
    ]
) }}

with

pre_excursions_x_zones as ( -- Croisement spatial des positions courantes des navires avec les zones maritimes
    select 
        distinct 
        excursion_id,
        zone_id
    from {{ ref('itm_zones_x_tracks_list')}}
    where zone_category = 'amp' -- Filtrage par catégorie de zone
    order by zone_id, excursion_id
),

excursions as (
    select 
        ex.vessel_id,ex.excursion_id, 
        ex.excursion_line,
        ex.excursion_line_metric/*, 
        excursion_start_position_id, 
        excursion_end_position_id,
        excursion_start_position_timestamp,
        excursion_end_position_timestamp
        excursion_status*/
    from {{ ref('itm_vessel_excursions') }} ex
    join pre_excursions_x_zones p on ex.excursion_id = p.excursion_id
),

zones as ( -- Chargement des zones maritimes
    select 
        z.zone_id,
        z.zone_category,
        z.zone_sub_category,
        z.zone_geometry,
        z.zone_geometry_metric
    from {{ ref('itm_dim_zones') }} z
    join pre_excursions_x_zones p on z.zone_id = p.zone_id
),



excursions_x_zones as ( -- Croisement spatial des positions courantes des navires avec les zones maritimes
    select
        ex.*,
        z.zone_id,
        z.zone_category,
        z.zone_sub_category--,
        -- ST_intersection(ex.excursion_line, z.zone_geometry) as track_in_zone
    from excursions ex
    join zones z on  true
        where exists (
            select 1 from pre_excursions_x_zones p
            where p.excursion_id = ex.excursion_id
                and p.zone_id = z.zone_id
        )
)

select * from excursions_x_zones