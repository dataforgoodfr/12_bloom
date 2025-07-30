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
    id as vessel_id,
    mmsi as dim_mmsi_mmsi,
    {{ switch_date_formats('start_date') }} as dim_mmsi_start_date,
    ({{ switch_date_formats('end_date') }} + interval '1 day' - interval '1 microsecond') as dim_mmsi_end_date,
    'HISTORICAL'::varchar as dim_mmsi_origin,
    details as dim_mmsi_details,
    now() as dim_mmsi_created_at
from {{ ref('historical_dim_mmsi') }}

where id is not NULL
