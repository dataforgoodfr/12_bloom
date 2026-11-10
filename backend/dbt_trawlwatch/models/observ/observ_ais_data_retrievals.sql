-- observ_ais_data_retrievals.sql
-- This file is used to create a tracking table for AIS data retrievals from Spire/Kpler.
/*
    Remontées d'API distincts des données AIS de Spire/Kpler (fondées sur created_at)
*/
{{ config(
    schema='observ',
    materialized='incremental',
    tags=['observ','ais', 'api_retrievals'],
    indexes=[
        {"columns": ["ais_retrieval_ts"], "type": "btree", "unique": True},
        {"columns": ["ais_retrieval_count"], "type": "btree"},
        {"columns": ["distinct_mmsi_count"], "type": "btree"},
        {"columns": ["observ_ais_data_retrievals_created_at"], "type": "btree"},
        {"columns": ["position_timestamp_min"], "type": "btree"},
        {"columns": ["position_timestamp_max"], "type": "btree"}
    ]
) }}

with

ais_data_retrievals as (
    select 
        created_at as ais_retrieval_ts,
        count(*) as ais_retrieval_count, -- Nombre de mesures remontées
        min(position_timestamp) as position_timestamp_min,
        max(position_timestamp) as position_timestamp_max,
        count(distinct vessel_mmsi) as distinct_mmsi_count,
        now() as observ_ais_data_retrievals_created_at
    from {{ source('kpler', 'kpler_ais_data') }}
    where created_at is not null
    {% if is_incremental() %}
        and created_at > (select max(ais_retrieval_ts) from {{ this }})
    {% endif %}
    group by created_at
)

select * from ais_data_retrievals 
order by ais_retrieval_ts desc