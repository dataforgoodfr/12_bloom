-- stg_spire_vessel_infos.sql
-- This file is used to create a kind of staging table for vessel information from the Spire API.

/*
    observ_spire_dim_vessel_configs permet de lister toutes les configs différentes des navires dans les données AIS de Spire
    avec des first_seen et last_seen.
    stg_spire_vessel_infos cherche à déterminer : 
    - si des configs se chevauchent pour un même navire
    - si plusieurs configs sont présentes pour un même navire à un instant T
    - la fréquence d'apparition des configs pour un navire donné
    - la fréquence de la config active (last_seen = max(last_seen)) pour un navire donné sur les 100 dernières remontées
*/

{{ config(
    enabled = true,
    schema = 'staging',
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['vessel_mmsi', 'config_hash'],
    tags = ['staging', 'ais','vessel_infos'],
    indexes = [
        {"columns": ["vessel_mmsi"], "type": "btree"},
        {"columns": ["vessel_mmsi", "config_hash"], "type": "btree"},
        {"columns": ["config_start", "config_end"], "type": "btree"}
    ],
) }}


with configs as (
    select 
        vessel_mmsi,
        config_hash,
        vessel_identification_infos
    from {{ ref('observ_spire_dim_vessel_configs') }}
),

ais_tagged as (
    select 
        s.vessel_mmsi,
        date_trunc('day',s.position_timestamp) as position_timestamp_day,
        date_trunc('day',s.created_at) as ais_message_retrieved_at_day,
        c.config_hash,
        c.vessel_identification_infos
    from {{ source('spire', 'spire_ais_data') }} as s
    join configs as c
      on jsonb_build_object(
            'vessel_imo', cast(s.vessel_imo as text),
            'vessel_name', cast(s.vessel_name as text),
            'vessel_callsign', cast(s.vessel_callsign as text),
            'vessel_flag', cast(s.vessel_flag as text),
            'vessel_length', s.vessel_length
         ) = c.vessel_identification_infos
    {% if is_incremental() %}
    where s.created_at > (select max(stg_spire_vessel_infos_created_at) from {{ this }})
    {% endif %}
),

tagged_with_breaks as (
    select *,
        case
            when lag(config_hash) over (partition by vessel_mmsi order by position_timestamp_day) = config_hash then 0
            else 1
        end as is_new_group
    from ais_tagged
),

tagged_with_group as (
    select *,
        sum(is_new_group) over (partition by vessel_mmsi order by position_timestamp_day rows unbounded preceding) as grp
    from tagged_with_breaks
),

final_configs as (
    select
        vessel_mmsi,
        config_hash,
        vessel_identification_infos,
        min(position_timestamp_day) as config_start,
        max(position_timestamp_day) as config_end,
        min(ais_message_retrieved_at_day) as ais_message_started_at_day,
        max(ais_message_retrieved_at_day) as ais_message_ended_at_day,
        count(*) as nb_messages
    from tagged_with_group
    group by vessel_mmsi, config_hash, grp, vessel_identification_infos
), with_lag as (
    select *,
        lag(config_end) over (partition by vessel_mmsi, config_hash order by config_start) as prev_config_end
    from final_configs
),

final_merged as (
    select 
        vessel_mmsi,
        config_hash,
        vessel_identification_infos,
        min(config_start) as config_start,
        max(config_end) as config_end,
        min(ais_message_started_at_day) as ais_message_started_at_day,
        max(ais_message_ended_at_day) as ais_message_ended_at_day,
        sum(nb_messages) as nb_messages
    from (
        select *,
            sum(
                case 
                    when prev_config_end = config_start then 0 
                    else 1 
                end
            ) over (
                partition by vessel_mmsi, config_hash 
                order by config_start 
                rows unbounded preceding
            ) as merged_grp
        from with_lag
    ) t
    group by vessel_mmsi, config_hash, vessel_identification_infos, merged_grp
)

select
    vessel_mmsi,
    config_hash,
    config_start,
    config_end,
    ais_message_started_at_day,
    ais_message_ended_at_day,
    vessel_identification_infos,
    vessel_identification_infos ->> 'vessel_imo'       as vessel_imo,
    vessel_identification_infos ->> 'vessel_name'      as vessel_name,
    vessel_identification_infos ->> 'vessel_callsign'  as vessel_callsign,
    vessel_identification_infos ->> 'vessel_flag'      as vessel_flag,
    (vessel_identification_infos ->> 'vessel_length')::numeric as vessel_length,
    now() as stg_spire_vessel_infos_created_at
from final_merged
