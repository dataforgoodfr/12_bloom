-- itm_zone_fishing_rights.sql
-- This model creates a view for fishing rights by flag associated with zones.
{{ config(
    schema='itm',
    materialized='table',
    tags=['dim', 'zones', 'fishing_rights']
) 
}}

select
  zone_id,
  zone_category,
  zone_sub_category,
  case 
    when zone_json_data->>'beneficiaries' is not null
      then string_to_array(zone_json_data->>'beneficiaries', ', ')
    when zone_category in ('Territorial seas', 'Fishing coastal waters (6-12 NM)', 'Clipped territorial seas')
      then array['FRA']
    when zone_category = 'amp'
      then null  -- accès par tous si aucun bénéficiaire désigné, sous réserve des droits des autres zones ?
    --else null
  end as beneficiaries
from {{ ref('stg_dim_zones') }}
