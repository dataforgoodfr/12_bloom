-- itm_ports_calls.sql

{{
    config(
        schema='itm',
        materialized='view',
        tags=['itm', 'vessel', 'visits_at_port'],
        indexes=[
            {'columns': ['port_id'], 'type': 'btree'},
            {'columns': ['port_name'], 'type': 'btree'},
            {'columns': ['port_locode'], 'type': 'btree'},
            {'columns': ['port_country'], 'type': 'btree'},
            {'columns': ['port_calls_count'], 'type': 'btree'},
            {'columns': ['total_port_call_duration'], 'type': 'btree'},
            {'columns': ['has_excursions'], 'type': 'btree'}
            
        ]
    )

}}

with

ports as ( -- Liste des ports
    select 
        *
    from {{ ref('itm_dim_ports') }}

),

port_calls as ( -- Escales au port
    select 
        distinct excursion_port_arrival, vessel_id, excursion_end_position_timestamp, excursion_id,
        lead(itm_vessel_excursions.excursion_id) over (partition by vessel_id order by excursion_id) as next_excursion_id
    from {{ ref('itm_vessel_excursions') }} 
),

excursion_port_departures as ( -- Départs du port
    select 
        distinct excursion_port_departure, vessel_id, excursion_start_position_timestamp, excursion_id
    from {{ ref('itm_vessel_excursions') }} 
),

calculating_port_calls as ( -- Calcul des escales
    select 
        pc.vessel_id,
        pc.excursion_port_arrival,
        pc.excursion_end_position_timestamp as port_call_start_at,
        pd.excursion_start_position_timestamp as port_call_end_at,
        case 
            when pd.excursion_start_position_timestamp is not null 
                    and pd.excursion_start_position_timestamp - pc.excursion_end_position_timestamp > interval '0 seconds'
                then pd.excursion_start_position_timestamp - pc.excursion_end_position_timestamp
        else null end as port_call_duration
    from  port_calls pc
    left join excursion_port_departures pd
     on pc.vessel_id = pd.vessel_id
     and pc.next_excursion_id = pd.excursion_id
),

port_call_synthesis as (
    select excursion_port_arrival as port_id,
    count(distinct vessel_id) as port_calls_count,
    sum(port_call_duration) as total_port_call_duration,
    true::boolean as has_excursions
    from calculating_port_calls
    group by excursion_port_arrival
),

port_visits as ( -- Visites au port
    select 
        ports.port_id,
        ports.port_name,
        ports.port_locode,
        ports.port_country_iso3,
        ports.port_latitude,
        ports.port_longitude,
        ports.port_url,
        ports.port_geometry_point,
        ports.port_geometry_buffer,
        coalesce(pcs.port_calls_count, 0) as port_calls_count,
        coalesce(pcs.total_port_call_duration, interval '0 seconds') as total_port_call_duration,
        coalesce(pcs.has_excursions, false) as has_excursions
    from ports
    left join port_call_synthesis pcs
        on ports.port_id = pcs.port_id
)

select * from port_visits
