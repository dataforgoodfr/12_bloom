-- itm_vessel_last_raw_position.sql
/*
    Retourne la liste des dernières positions RAW des navires (source directe spire_ais_data) pour chaque navire.
    Vessel_id est associé par jointure avec itm_dim_vessels sur le MMSI + l'IMO (pour tenir compte des réaffectations de MMSI).
    2 méthodes complémentaires pour récupérer la dernière position :
    - La dernière position de la dernière remontée AIS (env. 2/3 des navires)
    - La dernière position connue pour le navire, même si elle n'est pas de la dernière remontée (avec filtre incrémental sur created_at).  
    En cas d'absence de position de la dernière remontée, on utilise la dernière position connue pour le navire.
    Performance attendue : 5 à 6' en initialisation, < 10" en incrémental.
*/

{{ config(
    schema = 'itm',
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['vessel_id'],
    indexes = [
        {'columns': ['vessel_id'], 'type': 'btree', 'unique': True},
        {'columns': ['position_timestamp__raw_last'], 'type': 'btree'},
        {'columns': ['position_ais_created_at__raw_max'], 'type': 'btree'}
    ],
    pre_hook = [
        "SET work_mem = \'64MB\';"
    ]
) }}


with 

dim_vessels_mmsi as ( -- Nécessaire pour récupérer l'IMO
    select 
        dv.vessel_id,
        dm.dim_mmsi_mmsi,
        dv.dim_vessel_imo
    from {{ ref('stg_dim_vessels') }} as dv
    left join {{ ref('stg_dim_mmsi') }} as dm 
        on dv.vessel_id = dm.vessel_id
    where dv.dim_vessel_end_date is null and dm.dim_mmsi_end_date is null
),

last_spire_upd as ( -- Récupération de la dernière date de mise à jour des positions AIS
    select spire_retrieval_ts
    from {{ ref('observ_spire_ais_data_retrievals') }}
    order by spire_retrieval_ts desc
    limit 1
),

latest_raw as ( -- Récupérer uniquement les messages AIS de la dernière remontée
    select 
        s.vessel_mmsi as vessel_mmsi,
        cast(s.vessel_imo as varchar) as vessel_imo,
        s.created_at,
        s.position_timestamp,
        s.position_latitude,
        s.position_longitude,
        s.position_speed,
        s.position_heading,
        s.position_course,
        s.position_rot,
        cast('Last_AIS retrieval' as varchar) as last_raw_position_origin
    from {{ source('spire', 'spire_ais_data') }} as s
    inner join last_spire_upd on s.created_at = last_spire_upd.spire_retrieval_ts
),

latest_raw_with_id as ( -- Jointure gauche : les navires sont associés à la position de dernière remontée quand dispo
    select 
        dvm.vessel_id,
        dvm.dim_mmsi_mmsi,
        dvm.dim_vessel_imo,
        l.*
    from dim_vessels_mmsi as dvm
    left join latest_raw as l on 
        dvm.dim_mmsi_mmsi = l.vessel_mmsi and dvm.dim_vessel_imo = l.vessel_imo

),

vessels_no_latest_raw as ( -- Lister les navires sans position de dernière remontée
    select 
        vessel_id,
        dim_mmsi_mmsi,
        dim_vessel_imo
    from latest_raw_with_id
    where position_timestamp is null
),

last_pos_ts_per_ship as (
    select 
        s.vessel_mmsi,
        cast(s.vessel_imo as text) as vessel_imo,
        max(s.position_timestamp) as position_timestamp
    from {{ source('spire', 'spire_ais_data') }} as s
    {% if is_incremental() %}
        where created_at > (select max(position_ais_created_at__raw_max) from {{ this }})
    {% endif %}
    group by s.vessel_mmsi, s.vessel_imo
),

fallback_last_raw as (
    select 
        vnlr.vessel_id,
        s.vessel_mmsi,
        s.position_timestamp,
        s.position_latitude,
        s.position_longitude,
        s.position_speed,
        s.position_heading,
        s.position_course,
        s.position_rot,
        s.created_at,
        cast('Fallback last AIS position' as varchar) as last_raw_position_origin
    from vessels_no_latest_raw as vnlr
    inner join last_pos_ts_per_ship as lps
        on vnlr.dim_mmsi_mmsi = lps.vessel_mmsi
       and vnlr.dim_vessel_imo = lps.vessel_imo
    inner join (
        select 
            *,
            row_number() over (
                partition by vessel_mmsi, vessel_imo, position_timestamp
                order by created_at desc
            ) as rn
        from {{ source('spire', 'spire_ais_data') }}
        
    ) as s
       on s.vessel_mmsi = lps.vessel_mmsi
       and cast(s.vessel_imo as text) = lps.vessel_imo
       and s.position_timestamp = lps.position_timestamp
       and s.rn = 1
)

select 
    lrwi.vessel_id,
    coalesce(lrwi.position_timestamp, flr.position_timestamp) as position_timestamp__raw_last,
    coalesce(lrwi.vessel_mmsi, flr.vessel_mmsi) as position_mmsi__raw_last,
    coalesce(lrwi.position_latitude, flr.position_latitude) as position_latitude__raw_last,
    coalesce(lrwi.position_longitude, flr.position_longitude) as position_longitude__raw_last,
    coalesce(lrwi.position_speed, flr.position_speed) as position_speed__raw_last,
    coalesce(lrwi.position_heading, flr.position_heading) as position_heading__raw_last,
    coalesce(lrwi.position_course, flr.position_course) as position_course__raw_last,
    coalesce(lrwi.position_rot, flr.position_rot) as position_rot__raw_last,
    coalesce(lrwi.created_at, flr.created_at) as position_ais_created_at__raw_max,

    to_char(coalesce(lrwi.position_timestamp, flr.position_timestamp), 'YYYYMM') as position_timestamp__raw_max_month,
    date_trunc('day', coalesce(lrwi.position_timestamp, flr.position_timestamp)) as position_timestamp__raw_max_day,
    st_setsrid(
        st_makepoint(
            coalesce(lrwi.position_longitude, flr.position_longitude),
            coalesce(lrwi.position_latitude, flr.position_latitude)
        ), 4326) as position_point__raw_last,
    now() as last_raw_position_evaluated_at,
    coalesce(lrwi.last_raw_position_origin, flr.last_raw_position_origin) as last_raw_position_origin
from latest_raw_with_id as lrwi
left join fallback_last_raw as flr
    on lrwi.vessel_id = flr.vessel_id
order by lrwi.vessel_id
