-- itm_vessel_flags.sql
-- This model creates a view for vessel flags, with start and end dates.
{{ config(
    schema='itm',
    materialized='view',
    tags=['dim', 'vessels', 'flags','fishing_rights']
) 
}}


select
  vessel_id,
  dim_vessel_flag as vessel_flag,
  dim_vessel_start_date as flag_start_at,
  coalesce(dim_vessel_end_date, NULL) as flag_end_at
from {{ ref('stg_dim_vessels') }}
order by vessel_id, flag_start_at