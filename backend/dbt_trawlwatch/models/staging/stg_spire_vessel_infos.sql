-- stg_spire_vessel_infos.sql
-- This file is used to create a staging table for vessel information from the Spire API.

/*
    Détecter les changements dans la table Spire sur les données des navires associées à un MMSI
    1. Passer les champs non agrégés hors MMSI en JSONB
    2. Comparer current et lead
    3. Si changement, pointer la date de début et de fin de la configuration

    -- DEVELOPPEMENT A TERMINER...
*/

{{ config(
    enabled = true,
    schema = 'staging',
    materialized = 'incremental'
) }}

-- Utiliser pour les run d'initialisation
{% if not is_incremental() %}
    {% set partial_end_date = var('partial_end_date', '2099-12-31') %} 
{% endif %}


with

spire_vessel_infos as ( --Création d'une signature JSONB pour les infos d'identification hors MMSI de chaque navire
    select
        vessel_mmsi,
        position_timestamp,
        created_at as ais_message_retrieved_at,
        jsonb_build_object(
            'vessel_imo', vessel_imo,
            'vessel_name', vessel_name,
            'vessel_callsign', vessel_callsign,
            'vessel_flag', vessel_flag,
            'vessel_length', vessel_length
        ) as vessel_identification_infos
    from {{ source('spire', 'spire_ais_data') }}
    where true
    {% if is_incremental() %}
        and created_at > (select max(stg_spire_vessel_infos_created_at) from {{ this }})
    {% else %}
    -- Gestion du filtre de run partiel pour éviter les timeouts
        and created_at <= '{{ partial_end_date }}'
    {% endif %}
),

ordered as ( -- Récupération du JSONB contenant les infos d'identification du navire pour le message AIS précédent
    select 
        *,
        lag(vessel_identification_infos) over (partition by vessel_mmsi order by position_timestamp) as vessel_identification_infos_prev
    from spire_vessel_infos
),

change_flagged as ( -- Si les infos d'identification du navire ont changé, on marque le message AIS comme une nouvelle configuration
    select 
        *,
        case when vessel_identification_infos != vessel_identification_infos_prev then 1 else 0 end as is_new_config
    from ordered
),

diff_explained as (
    select 
        *,
        case when (vessel_identification_infos ->> 'vessel_imo') != (vessel_identification_infos_prev ->> 'vessel_imo') then 'vessel_imo,' else '' end ||
        case when (vessel_identification_infos ->> 'vessel_name') != (vessel_identification_infos_prev ->> 'vessel_name') then 'vessel_name,' else '' end ||
        case when (vessel_identification_infos ->> 'vessel_callsign') != (vessel_identification_infos_prev ->> 'vessel_callsign') then 'vessel_callsign,' else '' end ||
        case when (vessel_identification_infos ->> 'vessel_flag') != (vessel_identification_infos_prev ->> 'vessel_flag') then 'vessel_flag,' else '' end ||
        case when (vessel_identification_infos ->> 'vessel_length') != (vessel_identification_infos_prev ->> 'vessel_length') then 'vessel_length,' else '' end
        as changed_fields_raw
    from ordered
),

diff_explained_cleaned as (
    select 
        *,
        string_to_array(trim(trailing ',' from changed_fields_raw), ',') as changed_fields
    from diff_explained
),

configs as (
    select 
        change_flagged.*,
        sum(change_flagged.is_new_config) over (partition by change_flagged.vessel_mmsi order by change_flagged.position_timestamp) as config_seq,
        diff_explained_cleaned.changed_fields
    from change_flagged
    left join diff_explained_cleaned
        on change_flagged.vessel_mmsi = diff_explained_cleaned.vessel_mmsi
        and change_flagged.position_timestamp = diff_explained_cleaned.position_timestamp
),

final_configs as (
    select
        vessel_mmsi,
        min(position_timestamp) as config_start,
        max(position_timestamp) as config_end,
        min(ais_message_retrieved_at) as ais_message_started_at,
        max(ais_message_retrieved_at) as ais_message_ended_at,
        vessel_identification_infos,
        changed_fields
    from configs
    group by vessel_mmsi, config_seq, vessel_identification_infos, changed_fields
)

select 
    vessel_mmsi,
    config_start,
    config_end,
    ais_message_started_at,
    ais_message_ended_at,
    vessel_identification_infos,
    changed_fields,
    vessel_identification_infos ->> 'vessel_imo'       as vessel_imo,
    vessel_identification_infos ->> 'vessel_name'      as vessel_name,
    vessel_identification_infos ->> 'vessel_callsign'  as vessel_callsign,
    vessel_identification_infos ->> 'vessel_flag'      as vessel_flag,
    (vessel_identification_infos ->> 'vessel_length')::numeric as vessel_length,
    now() as stg_spire_vessel_infos_created_at
from final_configs
order by vessel_mmsi, config_start
