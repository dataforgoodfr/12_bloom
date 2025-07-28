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
    to_timestamp(start_date, 'DD/MM/YYYY') as dim_mmsi_start_date,
    (to_timestamp(end_date, 'DD/MM/YYYY') + interval '1 day' - interval '1 microsecond') as dim_mmsi_end_date,
    'HISTORICAL'::varchar as dim_mmsi_origin,
    details as dim_mmsi_details,
    now() as dim_mmsi_created_at
from {{ ref('historical_dim_mmsi') }}

where vessel_id is not null