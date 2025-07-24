-- itm_dim_vessels.sql
-- This models creates an intermediate view for Vessels.
/*
    A faire évoluer pour intégrer des insights d'observability à partir de obs_dim_vessels_consolidate
*/

{{ config(
    schema='itm',
    materialized='view',
    tags=['itm','dim', 'vessels']
) 
}}

with 

staged_vessels  as (select * from {{ ref('seed_dim_vessels') }})

select * from staged_vessels
order by vessel_id, mmsi