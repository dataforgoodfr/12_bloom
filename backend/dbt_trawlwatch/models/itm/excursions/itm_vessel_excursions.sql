-- itm_vessel_excursions.sql

/*
    Extract les positions des navires à l'intérieur des ports, détecte les entrées et sorties de port pour construire les excursions.
*/

{{ config(
    schema='itm',
    materialized='table',
    unique_key=['excursion_id'],
    tags=['itm', 'vessel', 'excursions'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['excursion_start_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_end_position_timestamp'], 'type': 'btree'},
        {'columns': ['excursion_port_departure'], 'type': 'btree'},
        {'columns': ['excursion_port_arrival'], 'type': 'btree'},
        {'columns': ['excursion_is_loop'], 'type': 'btree'},
        {'columns': ['excursion_duration_interval'], 'type': 'btree'},
        {'columns': ['excursion_status'], 'type': 'btree'}
    ]
) }}

{% set itm_vessel_positions_ref = adapter.get_relation(
        database=target.database,
        schema='itm',
        identifier='itm_vessel_positions'
) %}



with 

itm_vessel_excursions_events as ( -- Positions des navires filtrées : 1 par timestamp (hors station au port et doublons)
    select 
        position_id as position_id,
        vessel_id,
        position_timestamp,
        position_timestamp_day,
        position_timestamp_month,
        port_id,
        port_exited,
        is_first_position,
        is_last_position,
        is_excursion_start,
        is_excursion_end,
        position,
        position_itm_created_at as position_itm_created_at,
        case 
                when is_excursion_start then 'start'
                when is_excursion_end then 'end'
                when is_first_position then 'first'
                else 'unknown' end as excursion_event_type
    from ( select * from {{ ref('itm_vessel_positions') }} ) as itm_vessel_positions
    where (is_excursion_end = true or is_excursion_start = true or is_first_position = true)
    order by vessel_id, position_timestamp

),

check_next_excursion_event as ( -- Vérification du type d'événement d'excursion suivant pour chaque navire
    select 
        vessel_id,
        position_timestamp,
        position_timestamp_day,
        position_timestamp_month,
        position_id,
        port_id,
        port_exited,
        is_first_position,
        is_last_position,
        is_excursion_start,
        is_excursion_end,
        position_itm_created_at,
        excursion_event_type,
        lead(excursion_event_type) over (partition by vessel_id order by position_timestamp) as next_excursion_event_type
    from itm_vessel_excursions_events
),

/* Gestion des cas de succession des excursions :
Si le 1er excursion_event_type est un first_position mais le second un start : on ignore le first_position
Si le 1er excursion_event_type est un first_position mais le second un end : on garde le first_position qui devient le start
Si le 1er excursion_event_type est un start mais le second un end :  on garde tel quel
*/

treat_next_excursion_event as ( -- Traite le type d'événement d'excursion suivant pour chaque navire
    select 
        vessel_id,
        position_timestamp,
        position_timestamp_day,
        position_timestamp_month,
        position_id,
        port_id,
        port_exited,
        is_first_position,
        is_last_position,
        is_excursion_start,
        is_excursion_end,
        position_itm_created_at,
        excursion_event_type,
        case 
            when excursion_event_type = 'first' and next_excursion_event_type = 'start' then 'first'
            when excursion_event_type = 'first' and next_excursion_event_type = 'end' then 'start'
            when excursion_event_type = 'first' and next_excursion_event_type is null then 'start'

            when excursion_event_type = 'start' and next_excursion_event_type = 'end' then 'start'
            when excursion_event_type = 'start' and next_excursion_event_type = 'first' then 'ERROR_first_after_start'
            when excursion_event_type = 'start' and next_excursion_event_type = 'start' then 'ERROR_start_after_start'
            when excursion_event_type = 'start' and next_excursion_event_type is null then 'start'

            when excursion_event_type = 'end' and next_excursion_event_type = 'start' then 'end'
            when excursion_event_type = 'end' and next_excursion_event_type is null then 'end'
            when excursion_event_type = 'end' and next_excursion_event_type = 'end' then 'ERROR_end_after_end'
            when excursion_event_type = 'end' and next_excursion_event_type = 'first' then 'ERROR_first_after_end'
      
            when excursion_event_type = 'unknown' then 'unknown'
            else excursion_event_type end as excursion_event_type_redefined,
            next_excursion_event_type
    from check_next_excursion_event
),


filter_start_end as ( -- Filtre les événements d'excursion pour ne garder que les 'start' et 'end'
	select 
		*,
		row_number() over (partition by vessel_id order by position_timestamp) as excursion_event_rank
	from treat_next_excursion_event
	where excursion_event_type_redefined in ('start','end')
),


eval_start_end as ( -- A utiliser comme dernier CTE pour vérifier la succession des événements d'excursion (pruné par défaut car unused dans la suite du modèle)
	select *, case when excursion_event_rank %2 = 1 then 'expect start' else 'expect end' end as excursion_event_expected
	from filter_start_end
),

start_list as ( -- Liste des positions de début d'excursion
	select 
		position_id as excursion_start_position_id,
		position_timestamp as excursion_start_position_timestamp,
        position_timestamp_day as excursion_start_position_timestamp_day,
        position_timestamp_month as excursion_start_position_timestamp_month,
        vessel_id,
        port_id as excursion_start_port_id,
		excursion_event_rank,
        position_itm_created_at as excursion_start_position_itm_created_at
	from filter_start_end
	where excursion_event_type_redefined = 'start'
	order by vessel_id, excursion_start_position_id
),

end_list as ( -- Liste des positions de fin d'excursion
    select 
        position_id as excursion_end_position_id,
        position_timestamp as excursion_end_position_timestamp,
        position_timestamp_day as excursion_end_position_timestamp_day,
        position_timestamp_month as excursion_end_position_timestamp_month,
        vessel_id,
        port_id as excursion_end_port_id,
        excursion_event_rank,
        position_itm_created_at as excursion_end_position_itm_created_at
    from filter_start_end
    where excursion_event_type_redefined = 'end'
    order by vessel_id, excursion_end_position_id
),

join_it as ( -- Jointure des positions de début et de fin d'excursion
	select 
		s.*,
		e.excursion_end_position_id,
		e.excursion_end_position_timestamp,
		e.excursion_end_position_timestamp_day,
		e.excursion_end_position_timestamp_month,
		e.excursion_end_port_id,
		(e.excursion_end_position_timestamp - s.excursion_start_position_timestamp) as excursion_duration_interval,
         case 
            when e.excursion_end_position_timestamp is not null then 'completed'
            when s.excursion_start_position_timestamp is not null then 'ongoing'
            else 'unknown' 
        end as excursion_status, -- Statut de l'excursion
        s.vessel_id || '_' || lpad(s.excursion_event_rank::text, 4, '0')  as excursion_id,
        case 
        when excursion_start_port_id = excursion_end_port_id then true
        when excursion_start_port_id != excursion_end_port_id then false
        else null end as excursion_is_loop,

        case when s.excursion_start_position_itm_created_at > e.excursion_end_position_itm_created_at then s.excursion_start_position_itm_created_at
        else e.excursion_end_position_itm_created_at end as excursion_position_itm_created_at -- Date de création de l'excursion (la plus récente des 2 positions)

	from start_list s
	left join end_list e on s.vessel_id = e.vessel_id and s.excursion_event_rank + 1 = e.excursion_event_rank
)

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

    excursion_start_port_id as excursion_port_departure,
    excursion_end_port_id as excursion_port_arrival,
    excursion_is_loop,
    excursion_duration_interval,
    excursion_status,
    
    excursion_position_itm_created_at,
    now() as excursion_created_at -- Date de création de l'excursion

from join_it order by vessel_id, excursion_id
