-- seed_historical_dim_mmsi.sql
/*
    Table de staging des liens MMSI - vessel_id historisés.
*/

{{ config(
    schema='staging',
    materialized='view',
    tags=['seed','dim', 'mmsi','historical']
) 
}}

select
    vessel_id as vessel_id,
    mmsi as dim_mmsi_mmsi,
    start_date as dim_mmsi_start_date,
    end_date as dim_mmsi_end_date,
    'HISTORICAL'::varchar as dim_mmsi_origin,
    now() as dim_mmsi_created_at
from {{ ref('dim_mmsi') }}

where vessel_id is not null