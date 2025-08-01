-- itm_vessel_excursions_details.sql
-- This model aggregates vessel excursions with their positions, providing a comprehensive view of each excursion's details
{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    schema='itm',
    unique_key=['excursion_id'],
    tags=['itm', 'vessel', 'excursions', 'details'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_end_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_port_departure'], 'type': 'btree'},
        {'columns': ['excursion_port_arrival'], 'type': 'btree'},
        {'columns': ['excursion_is_loop'], 'type': 'btree'},
        {'columns': ['excursion_duration_interval'], 'type': 'btree'},
        {'columns': ['excursion_status'], 'type': 'btree'},
        {'columns': ['excursion_position_itm_created_at'], 'type': 'btree'},
        {'columns': ['excursion_line'], 'type': 'gist'},
        {'columns': ['excursion_line_metrics'], 'type': 'gist'}
    ],
    pre_hook="set work_mem to '64MB';"
)
}}

WITH excursions AS (

    -- Excursions à détailler
    SELECT *
    FROM {{ ref('itm_vessel_excursions') }}
    {% if is_incremental() %}
    WHERE excursion_created_at >= (
            SELECT COALESCE(MAX(excursion_details_completed_at), '2000-01-01')
            FROM {{ this }}
          )
    {% endif %}

),

positions AS (

    -- On ne garde que les positions nécessaires
    SELECT *
    FROM {{ ref('itm_vessel_positions') }}
    WHERE position_point IS NOT NULL
    {% if is_incremental() %}
      AND position_itm_created_at >= (
            SELECT COALESCE(MAX(excursion_position_itm_created_at), '2000-01-01')
            FROM {{ this }}
          )
    {% endif %}

), 

joined AS (

    -- Jointure “one big set” : pas d’appel répétitif
    SELECT
        exc.*,
        pos.position_id,
        pos.position_timestamp,
        pos.position_point
    FROM excursions exc
    LEFT JOIN positions pos
      ON  pos.vessel_id = exc.vessel_id
      AND pos.position_timestamp BETWEEN exc.excursion_start_position_timestamp
                                     AND COALESCE(exc.excursion_end_position_timestamp, 'infinity')

)

SELECT
    ------------------------  Colonnes d’origine  ------------------------
    joined.vessel_id,
    joined.excursion_id,

    joined.excursion_start_position_id,
    joined.excursion_start_position_timestamp,
    joined.excursion_start_position_timestamp_day,
    joined.excursion_start_position_timestamp_month,

    joined.excursion_end_position_id,
    joined.excursion_end_position_timestamp,
    joined.excursion_end_position_timestamp_day,
    joined.excursion_end_position_timestamp_month,

    joined.excursion_port_departure,
    joined.excursion_port_arrival,
    joined.excursion_is_loop,
    joined.excursion_duration_interval,
    joined.excursion_status,
    joined.excursion_position_itm_created_at,
    joined.excursion_created_at,

    ------------------------  Agrégations  ------------------------
    ARRAY_AGG(joined.position_id ORDER BY joined.position_timestamp)      AS excursion_position_ids,
    COUNT(joined.position_id)                                             AS excursion_positions_count,
    MAX(joined.position_timestamp)                                        AS last_position_checked,

    ST_MakeLine(ARRAY_AGG(joined.position_point ORDER BY joined.position_timestamp))
        AS excursion_line,
    ST_Transform(
        ST_MakeLine(ARRAY_AGG(joined.position_point ORDER BY joined.position_timestamp)),
        3857
    )                                                                     AS excursion_line_metrics,

    ------------------------  Métadonnée  ------------------------
    NOW()                                                                 AS excursion_details_completed_at

FROM joined
GROUP BY
    joined.vessel_id,
    joined.excursion_id,

    joined.excursion_start_position_id,
    joined.excursion_start_position_timestamp,
    joined.excursion_start_position_timestamp_day,
    joined.excursion_start_position_timestamp_month,

    joined.excursion_end_position_id,
    joined.excursion_end_position_timestamp,
    joined.excursion_end_position_timestamp_day,
    joined.excursion_end_position_timestamp_month,

    joined.excursion_port_departure,
    joined.excursion_port_arrival,
    joined.excursion_is_loop,
    joined.excursion_duration_interval,
    joined.excursion_status,
    joined.excursion_position_itm_created_at,
    joined.excursion_created_at

/*
select
    exc.*,
    (f).position_ids as excursion_position_ids,
    (f).positions_count as excursion_positions_count,
    (f).last_position_checked,
    (f).excursion_line,
    (f).excursion_line_metrics,
    now() as excursion_details_completed_at
from {{ ref('itm_vessel_excursions') }} exc
left join lateral (
    select * from utils.get_excursion_details(
        cast(exc.vessel_id as varchar),
        exc.excursion_start_position_timestamp,
        exc.excursion_end_position_timestamp
    )
) f on true
{% if is_incremental() %}
where exc.excursion_created_at >= (select max(excursion_details_completed_at) from {{ this }})
{% endif %}
*/
/*
positions as ( 

    select *
    from {{ ref('itm_vessel_positions') }} 
    {% if is_incremental() %}
    where position_itm_created_at >= (select max(excursion_position_itm_created_at) from {{ this }})
    {% endif %}
),

excursions as (

    select 
        vessel_id,
        excursion_id,
        excursion_start_position_id,
        excursion_start_position_timestamp,
        excursion_start_position_timestamp_day,
        excursion_start_position_timestamp_month,
        excursion_end_position_id,
        excursion_end_position_timestamp,
        excursion_end_position_timestamp_day,
        excursion_end_position_timestamp_month,
        excursion_port_departure,
        excursion_port_arrival,
        excursion_is_loop,
        excursion_duration_interval,
        excursion_status,
        excursion_position_itm_created_at,
        excursion_created_at
    from {{ ref('itm_vessel_excursions') }}
),

excursions_detailed as (

    select 
        exc.*,

        array_agg(pos.position_id) as excursion_position_ids,
        count(pos.position_id) as excursion_positions_count,
        max(pos.position_timestamp) as last_position_checked,

        st_makeline(
            array_agg(pos.position_point order by pos.position_timestamp)
        ) as excursion_line

    from excursions as exc
    left join positions as pos 
        on exc.vessel_id = pos.vessel_id 
        /*
        and pos.position_timestamp_month between exc.excursion_start_position_timestamp_month and exc.excursion_end_position_timestamp_month
        and pos.position_timestamp_day between exc.excursion_start_position_timestamp_day and exc.excursion_end_position_timestamp_day
        and pos.position_timestamp between exc.excursion_start_position_timestamp and exc.excursion_end_position_timestamp*/
        and pos.position_timestamp is not NULL
        and (
            pos.position_timestamp_month >= exc.excursion_start_position_timestamp_month
            and (pos.position_timestamp_month <= exc.excursion_end_position_timestamp_month or exc.excursion_end_position_timestamp_month is NULL)
        )
        and utils.safe_between( pos.position_timestamp_day,  exc.excursion_start_position_timestamp_day, exc.excursion_end_position_timestamp_day)
        and utils.safe_between( pos.position_timestamp,  exc.excursion_start_position_timestamp, exc.excursion_end_position_timestamp)

    group by 
        exc.vessel_id,
        exc.excursion_id,
        exc.excursion_start_position_id, exc.excursion_end_position_id,
        exc.excursion_start_position_timestamp, exc.excursion_end_position_timestamp,
        exc.excursion_start_position_timestamp_day, exc.excursion_end_position_timestamp_day,
        exc.excursion_start_position_timestamp_month, exc.excursion_end_position_timestamp_month,
        exc.excursion_port_departure, exc.excursion_port_arrival,
        exc.excursion_is_loop, exc.excursion_duration_interval,
        exc.excursion_status, exc.excursion_created_at,
        exc.excursion_position_itm_created_at
),

excursions_synthesis as ( -- Synthèse des excursions (partie 1 : métriques non sensibles aux zones maritimes)
    select 
        -- source : excursions
        vessel_id, 
        excursion_id,

        excursion_start_position_id,
        excursion_start_position_timestamp,
        excursion_start_position_timestamp_day,
        excursion_start_position_timestamp_month,

        excursion_end_position_id,
        excursion_end_position_timestamp,
        excursion_end_position_timestamp_day,
        excursion_end_position_timestamp_month,

        excursion_port_departure,
        excursion_port_arrival,
        excursion_is_loop,
        excursion_duration_interval as total_time_at_sea,

        excursion_status,
        excursion_position_itm_created_at,
        excursion_created_at,

        excursion_position_ids,
        excursion_positions_count,
        round((extract(epoch from excursion_duration_interval) / excursion_positions_count::numeric )/60,1) as excursion_interval_between_positions_minutes,
        round(st_length(st_transform(excursion_line,3857))::numeric/1852.0, 3) as excursion_line_length_nm,
        last_position_checked,

        excursion_line,
        st_transform(excursion_line, 3857) as excursion_line_metric,

        now() as excursion_details_completed_at -- Date de MAJ de l'excursion

    from excursions_detailed

    
)

select * from excursions_synthesis
order by excursion_id
*/