-- itm_vessel_excursions_details.sql
-- This model aggregates vessel excursions with their positions, providing a comprehensive view of each excursion's details
{{ config(
    materialized='table',
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
    ]
)
}}

with 

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
        and utils.safe_between( pos.position_timestamp_month,  exc.excursion_start_position_timestamp_month, exc.excursion_end_position_timestamp_month)
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
