-- itm_vessel_segments_by_date.sql

/*
    Agrégation des segments de navires par date.
    Cette table est utilisée pour alimenter les marts concernant les données de synthèse des navires filtrées par date
*/

-- Si le batch size est défini sur 'hour', on utilise 'day' pour le microbatch
-- Sinon, on utilise 'month' pour le microbatch (env. 15"/mois de temps d'exécution)
{% set default_batch_size = var('default_microbatch_size', 'month') %}
{% if default_batch_size == 'hour' %}
    {% set batchsize = 'day' %}
{% else %}
    {% set batchsize = 'month' %}
{% endif %}

{{ config(
    schema = 'itm',
    enabled = true,
    materialized = 'incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = batchsize,
    begin = '2024-05-01',
    unique_key = ['vessel_id', 'excursion_id','daysegments_date','segment_type'],
    indexes = [
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['daysegments_date'], 'type': 'btree'},
        {'columns': ['segment_type'], 'type': 'btree'},
        {'columns': ['daysegments_line'], 'type': 'gist'}
    ],

) }}

with

-- Récupération des segments de chaque navire
vessel_daysegments as (
    select 
        
        vessel_id, -- Identifiant du navire
        excursion_id, -- Identifiant de l'excursion
        segment_ends_at_day as daysegments_date, -- Date de fin du segment
        segment_type, -- Type de segment (AT_SEA, DEFAULT_AIS)

        sum(cast(segment_duration as interval)) as segment_duration, -- Interval
        sum(cast(segment_duration_s as bigint)) AS daysegments_duration_s, -- Durée du segment en secondes
        sum(cast(segment_duration_h as bigint)) AS daysegments_duration_h, -- Durée du segment en heures

        sum(segment_distance_m) AS daysegments_distance_m, -- Distance parcourue dans le segment en mètres (calculée entre les positions de début et de fin du segment)
        sum(segment_distance_nm) AS daysegments_distance_nm, -- Distance parcourue dans le segment en milles marins (calculée entre les positions de début et de fin du segment)

        avg(segment_average_speed) as daysegments_daily_average_speed, -- Vitesse moyenne du segment en nœuds (calculée en faisant la moyenne des vitesses AIS disponibles)
        avg(segment_course_speed) as daysegments_daily_course_speed, -- Vitesse de la route fond en nœuds (calculée entre les positions de début et de fin du segment)

        -- Intersection entre zone_ids et zone_ids_prev : les zones dans lesquelles le navire est resté entre les 2 positions
        utils.array_concat_uniq_agg(zones_crossed) as zones_crossed, 

        -- Le navire est-il dans une zone AMP ?
        sum(case when is_in_amp_zone then segment_duration else cast('0 minute' as interval) end) as time_in_amp_zone, 
        -- Le navire est-il dans des eaux territoriales ?
        sum(case when is_in_territorial_waters then segment_duration else cast('0 minute' as interval) end) as time_in_territorial_waters,
        -- Le navire est-il dans une zone pour laquelle il n'a pas de droit de pêche ? 
        sum(case when is_in_zone_with_no_fishing_rights then segment_duration else cast('0 minute' as interval) end) as time_in_zone_with_no_fishing_rights, 

        st_linemerge(st_collect(segment_line), TRUE) as daysegments_line-- Ligne géographique du segment (entre les positions de début et de fin), WGS84

    from {{ ref('itm_vessel_segments') }}
    group by 
        vessel_id,
        excursion_id,
        segment_ends_at_day,
        segment_type
)

select 
    vs.vessel_id,
    vs.excursion_id,
    vs.daysegments_date,
    vs.segment_type,
    vs.segment_duration,
    vs.daysegments_duration_s,
    vs.daysegments_duration_h,
    vs.daysegments_distance_m,
    vs.daysegments_distance_nm,
    vs.daysegments_daily_average_speed,
    vs.daysegments_daily_course_speed,
    vs.zones_crossed,
    vs.time_in_amp_zone,
    vs.time_in_territorial_waters,
    vs.time_in_zone_with_no_fishing_rights,
    vs.daysegments_line

from vessel_daysegments as vs
