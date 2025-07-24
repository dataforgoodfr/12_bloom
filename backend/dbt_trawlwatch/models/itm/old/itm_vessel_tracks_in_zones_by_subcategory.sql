-- itm_vessel_tracks_in_zones_by_subcategory.sql
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
        {'columns': ['tracks_in_zone'], 'type': 'gist'}
    ]
) }}

with 
cat_list as (
    select zone_category, zone_sub_category
    from {{ ref('itm_zones_categories') }}
)

select * from cat_list