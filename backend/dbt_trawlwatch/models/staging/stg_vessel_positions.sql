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

    La table est partitionnée et administrée par les fonctions :
        - staging.mange_stg_vessel_positions_partitions(), qui crée la table, les partitions initiales et les index
        - staging.ensure_stg_vessel_positions_future_partitions(), qui crée automatiquement les nouvelles partitions nécessaires

    [[[NE PAS UTILISER dbt run --full-refresh]]] sur ce modèle, car cela détruirait le partitionnement
    Pour une régénération complète : SELECT staging.manage_staging_vessel_positions_partitions(start_year,end_year, full_rebuild=true) (si changement de structure)
    puis dbt run --select staging.vessel_positions+ --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'

*/

{{ config(
    schema = 'staging',
    materialized = 'incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-05-01',
    unique_key = ['position_id', 'position_timestamp_month'],
    tags = ['staging', 'ais'],
    pre_hook="SELECT staging.ensure_stg_vessel_positions_future_partitions();",
    post_hook="ANALYZE {{ this }};"
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}
{% if mmsi_list | length > 0 %}
    {% set MMSI_filter = "and position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
    {% set MMSI_filter = "" %}
{% endif %}

with 

spire_source as ( -- Selectionner les mesures distinctes (MMSI, timestamp, latitude, longitude, etc.) de la source de données AIS
/* Dans le cas où plusieurs messages AIS sont reçus pour une même position, on ne garde que les dernières infos non nulles pour chaque champ    */

    select 
        vessel_mmsi as position_mmsi,
        date_trunc('second', position_timestamp) as position_timestamp,
        max(id) as position_id,
        (array_agg(position_latitude order by position_timestamp desc) filter (where position_latitude is not NULL))[1] as position_latitude, -- noqa: CP01
        (array_agg(position_longitude order by position_timestamp desc) filter (where position_longitude is not NULL))[1] as position_longitude,
        (array_agg(position_rot order by position_timestamp desc) filter (where position_rot is not NULL))[1] as position_rot,
        (array_agg(position_speed order by position_timestamp desc) filter (where position_speed is not NULL))[1] as position_speed,
        (array_agg(position_course order by position_timestamp desc) filter (where position_course is not NULL))[1] as position_course,
        (array_agg(position_heading order by position_timestamp desc) filter (where position_heading is not NULL))[1] as position_heading,
        min(created_at) as position_ais_created_at_min,
        max(created_at) as position_ais_created_at_max

    from (select * from {{ source('spire','spire_ais_data') }})  as s

    where 
        date_trunc('second', position_timestamp) is not NULL 
        and  date_trunc('second', position_timestamp) >= '2024-05-01 00:00:00'
        and position_latitude is not NULL
        and position_longitude is not NULL
        and vessel_mmsi is not NULL
        and created_at is not NULL
    group by
        date_trunc('second', position_timestamp),
        position_mmsi

),

def_partitions AS ( -- Définition des champs de partitions et indexation temporelle
    select 
        *,
        to_char(position_timestamp, 'YYYYMM') AS position_timestamp_month,
        date_trunc('day', position_timestamp)::date AS position_timestamp_day
    from spire_source
),

-- Etape 1 : Jointure des positions AIS avec la table de dimension des navires

vessels as (

    select * from {{ ref('stg_dim_mmsi') }} 

), 

join_spire_ais_and_vessels as ( -- On ne conserve que la dernière remontée AIS correspondant à la position

    select
        concat(v.vessel_id, '_', to_char(ais.position_timestamp, 'YYYYMMDD_HH24MISS')) as position_id,
        ais.position_timestamp,
        ais.position_mmsi,
        coalesce(v.vessel_id, 'UNKNOWN_MMSI='||ais.position_mmsi) as vessel_id,
        ais.position_latitude,
        ais.position_longitude,
        ais.position_speed,
        ais.position_heading,
        ais.position_course,
        ais.position_rot,
        ais.position_timestamp_month,
        ais.position_timestamp_day,
        ais.position_ais_created_at_min,
        ais.position_ais_created_at_max,
        st_setsrid(st_makepoint(ais.position_longitude, ais.position_latitude), 4326) as position_point
    from def_partitions as ais
    left join vessels as v
        on ais.position_mmsi = v.dim_mmsi_mmsi and utils.safe_between(ais.position_timestamp, v.dim_mmsi_start_date, v.dim_mmsi_end_date)
    where
        TRUE
        {{ MMSI_filter }}
        and ais.position_latitude is not NULL
        and ais.position_longitude is not NULL
        and ais.position_speed is not NULL
        and ais.position_heading is not NULL
        and ais.position_course is not NULL
        and ais.position_rot is not NULL
        and ais.position_timestamp is not NULL
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
    position_ais_created_at_min,
    position_ais_created_at_max,
    now() as position_stg_created_at,
    position_point
from join_spire_ais_and_vessels
where vessel_id not like 'UNKNOWN_MMSI=%'
order by position_timestamp, vessel_id
