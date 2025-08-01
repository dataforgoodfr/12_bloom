-- observ_spire_dim_vessel_configs.sql
-- This models tracks distinct configs for vessels in the Spire AIS data and gives a MD5 hash for each config
-- Used by stg_spire_vessel_infos
{{ config(
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['vessel_mmsi', 'config_hash'],
    schema = 'observ',
    tags = ['observ', 'ais', 'vessel_infos'],
    indexes = [
        {"columns": ["vessel_mmsi"], "type": "btree"},
        {"columns": ["vessel_mmsi", "config_hash"], "type": "btree", "unique": true}
    ]
) }}

with all_configs as (

    select
        s.vessel_mmsi,
        jsonb_build_object(
            'vessel_imo', cast(s.vessel_imo as text),
            'vessel_name', cast(s.vessel_name as text),
            'vessel_callsign', cast(s.vessel_callsign as text),
            'vessel_flag', cast(s.vessel_flag as text),
            'vessel_length', s.vessel_length 
        ) as vessel_identification_infos,
        s.created_at
    from {{ source('spire', 'spire_ais_data') }} s
    {% if is_incremental() %}
        where s.created_at >= (select max(last_seen) from {{ this }})
    {% endif %}
),

agg_configs as (

    select 
        ac.vessel_mmsi,
        ac.vessel_identification_infos,
        min(ac.created_at) as first_seen,
        max(ac.created_at) as last_seen,
        md5(ac.vessel_identification_infos::text) as config_hash,
        cast(null as boolean) as is_valid_config -- Placeholder for future use
    from all_configs ac
    group by ac.vessel_mmsi, ac.vessel_identification_infos
)

select agg_configs.* 
from agg_configs
{% if is_incremental() %}
    left join {{ this }} as existing
        on agg_configs.vessel_mmsi = existing.vessel_mmsi
        and agg_configs.config_hash = existing.config_hash
    where existing.vessel_mmsi is null
{% endif %}
order by agg_configs.vessel_mmsi, agg_configs.first_seen
