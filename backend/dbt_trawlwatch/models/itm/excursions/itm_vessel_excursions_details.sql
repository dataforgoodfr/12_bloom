-- itm_vessel_excursions_details.sql
-- This model aggregates vessel excursions with their positions, providing a comprehensive view of each excursion's details

{{ config(
    materialized='table',
    schema='itm'
) }}

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
        
        e.*,

        array_agg(p.position_id) as excursion_position_ids,
        count(p.position_id) as excursion_positions_count,
        max(position_timestamp) as last_position_checked,

        ST_MakeLine(
            array_agg(p.position order by p.position_timestamp)
        ) as excursion_line

    from excursions e
    left join positions p 
        on e.vessel_id = p.vessel_id 
        and p.position_timestamp_month between e.excursion_start_position_timestamp_month and e.excursion_end_position_timestamp_month
        and p.position_timestamp_day between e.excursion_start_position_timestamp_day and e.excursion_end_position_timestamp_day
        and p.position_timestamp between e.excursion_start_position_timestamp and e.excursion_end_position_timestamp
    group by 
        e.vessel_id,
        e.excursion_id,
        e.excursion_start_position_id, e.excursion_end_position_id,
        e.excursion_start_position_timestamp, e.excursion_end_position_timestamp,
        e.excursion_start_position_timestamp_day, e.excursion_end_position_timestamp_day,
        e.excursion_start_position_timestamp_month, e.excursion_end_position_timestamp_month,
        e.excursion_port_departure, e.excursion_port_arrival,
        e.excursion_is_loop, e.excursion_duration_interval,
        e.excursion_status, e.excursion_created_at,
        e.excursion_position_itm_created_at
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
        round ((extract(epoch from excursion_duration_interval) / excursion_positions_count::numeric )/60,1) as excursion_interval_between_positions_minutes,
        round(st_length(st_transform(excursion_line,3857))::numeric/1852.0, 3) as excursion_line_length_nm,
        last_position_checked,

        excursion_line,
        st_transform(excursion_line, 3857) as excursion_line_metric,

        now() as excursion_details_completed_at -- Date de MAJ de l'excursion

    from excursions_detailed

    
)


select * from excursions_synthesis
order by excursion_id
