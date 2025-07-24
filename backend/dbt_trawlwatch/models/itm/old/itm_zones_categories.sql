-- itm_zones_categories.sql
{{
    config(
        enabled = false,
        schema='itm',
        materialized='table',
        unique_key=['zone_category', 'zone_sub_category'],
        tags=['itm', 'zones', 'categories'],
        indexes=[
            {'columns': ['zone_category'], 'type': 'btree'},
            {'columns': ['zone_sub_category'], 'type': 'btree'}
        ]
    )
}}
select distinct zone_category, zone_sub_category
from {{ ref('itm_dim_zones') }}
where zone_category is not null
order by zone_category, zone_sub_category