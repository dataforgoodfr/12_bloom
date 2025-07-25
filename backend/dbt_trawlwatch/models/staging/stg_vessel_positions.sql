-- stg_vessel_positions.sql
-- This file is used to create a staging table for AIS vessel positions.

/*
    1. Extrait les dernières positions remontées dans la table public.spire_ais_data par micro-batch 
       (chaque batch filtre les données correspondant à une petite plage de temps, définie par batch_size sur position_timestamp)
    2. Jointure avec la table de référence des navires (seed_dim_vessels) sur le MMSI pour récupérer vessel_id
    3. Crée un point géographique à partir de la latitude et de la longitude
    4. Sélectionne les colonnes nécessaires pour la table de positions des navires
    5. Les ajoute dans le modèle incrémental des positions de navires


    La récupération d'un historique de positions se fait en lançant un microbatch suivant cet exemple (pour la période du 1er janvier au 15 juillet 2025) :
     dbt run -m  stg_vessel_positions --event-time-start "2025-01-01" --event-time-end "2025-07-15"
*/

{{ config(
    schema = 'staging',
    materialized = 'incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-05-01',
    lookback = 3,
    unique_key = ['position_id', 'position_timestamp_month'],
    pre_hook="SELECT staging.ensure_stg_vessel_positions_future_partitions();"
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}

{% if mmsi_list | length > 0 %}
  {% set MMSI_filter = "where position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
  {% set MMSI_filter = "" %}
{% endif %}


with 



spire_source as ( -- Selectionner les mesures distinctes (MMSI, timestamp, latitude, longitude, etc.) de la source de données AIS
/* Dans le cas où plusieurs messages AIS sont reçus pour une même position, on ne garde que les dernières infos non nulles pour chaque champ    */

    select 
        max(id) as position_id,
        vessel_mmsi as position_mmsi,
        date_trunc('second', position_timestamp) as position_timestamp,
        (ARRAY_AGG(position_latitude ORDER BY position_timestamp DESC) FILTER (WHERE position_latitude IS NOT NULL))[1] AS position_latitude,
        (ARRAY_AGG(position_longitude ORDER BY position_timestamp DESC) FILTER (WHERE position_longitude IS NOT NULL))[1] AS position_longitude,
        (ARRAY_AGG(position_rot ORDER BY position_timestamp DESC) FILTER (WHERE position_rot IS NOT NULL))[1] AS position_rot,
        (ARRAY_AGG(position_speed ORDER BY position_timestamp DESC) FILTER (WHERE position_speed IS NOT NULL))[1] AS position_speed,
        (ARRAY_AGG(position_course ORDER BY position_timestamp DESC) FILTER (WHERE position_course IS NOT NULL))[1] AS position_course,
        (ARRAY_AGG(position_heading ORDER BY position_timestamp DESC) FILTER (WHERE position_heading IS NOT NULL))[1] AS position_heading,
        min(created_at) as position_ais_created_at_min,
        max(created_at) as position_ais_created_at_max

    from (select * from {{ source('spire','spire_ais_data') }})  s

    where 
        date_trunc('second', position_timestamp) is not null and  date_trunc('second', position_timestamp) >= '2024-05-01 00:00:00'
        and position_latitude is not null
        and position_longitude is not null
        and vessel_mmsi is not null
        and created_at is not null
    group by
        date_trunc('second', position_timestamp),
        position_mmsi

),



def_partitions AS (
        SELECT *,
        to_char(position_timestamp, 'YYYYMM') AS position_timestamp_month,
        date_trunc('day', position_timestamp)::date AS position_timestamp_day,
        NOW() as position_stg_created_at
        FROM spire_source
),

-- Etape 1 : Jointure des positions AIS avec la table de dimension des navires

vessels as (

    select * from {{ ref('stg_dim_mmsi') }} 

), 

join_spire_ais_and_vessels as ( -- On ne conserve que la dernière remontée AIS correspondant à la position

    select
        CONCAT(vessel_id, '_', to_char(position_timestamp, 'YYYYMMDD_HH24:MI:SS')) as position_id,
        position_timestamp,
        position_mmsi,
        case when vessel_id is null then 'UNKNOWN_MMSI='||position_mmsi else vessel_id end as vessel_id,
        position_latitude,
        position_longitude,
        position_speed,
        position_heading,
        position_course,
        position_rot,
        position_timestamp_month,
        position_timestamp_day,
        position_stg_created_at,
        position_ais_created_at_min,
        position_ais_created_at_max,
        ST_SetSRID(ST_MakePoint(position_longitude, position_latitude), 4326) as position
    from def_partitions ais
    left join vessels v 
        on ais.position_mmsi = v.mmsi 
        and utils.safe_between(ais.position_timestamp, v.dim_mmsi_start_date, v.dim_mmsi_end_date)
    {{ MMSI_filter }}
    where position_latitude is not null
        and position_longitude is not null
        and position_speed is not null
        and position_heading is not null
        and position_course is not null
        and position_rot is not null
        and position_timestamp is not null
    {{ MMSI_filter }}
    order by position_timestamp desc
)


select distinct 
        position_id,
        position_timestamp,
        position_mmsi,
        vessel_id,
        position_latitude,
        position_longitude,
        position_speed,
        position_heading,
        position_course,
        position_rot,
        position_timestamp_month,
        position_timestamp_day,
        position_stg_created_at,
        position_ais_created_at_min,
        position_ais_created_at_max,
        position
        -- Ajouter un champ méta stg_position_created_at
from join_spire_ais_and_vessels
order by position_timestamp, vessel_id