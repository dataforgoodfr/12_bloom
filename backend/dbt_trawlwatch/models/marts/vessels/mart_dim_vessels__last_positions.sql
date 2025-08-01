-- mart_dim_vessels__last_positions.sql
/* This file is used to create a mart table for every vessel last positions for API route:
    - api/v1/vessels/all/positions/last : Return last positions of all vessels
    - api/v1/vessels/{vessel_id}/positions/last : Return last position of a specific vessel
    Fields:
    - vessel_id: Unique identifier of the vessel
    - mmsi: Active MMSI of the vessel
    - ship_name: Name of the vessel
    - width: Vessel width (in m)
    - length: Vessel length overall (in m)
    - country_iso3: Code of the country where the vessel is registered
    - type: Fishing vessel "type" (FAO gear subcategory or category)
    - imo: IMO number of the vessel, used as a unique identifier
    - cfr: CFR number of the vessel (EU identifier).
    - external_marking: External marking written on the hull
    - ircs: Call sign of the vessel, used for identification
    - tracking_activated: Indicates if the vessel is being tracked
    - tracking_status: Details on the vessel status (active, exported, wreck)
    - home_port_id: Most visited port: unique identifier for each port (based on UN/LOCODE)
    - vessel_created_at: Timestamp when the vessel record was created in the database
    - vessel_updated_at: Timestamp when the vessel record was last updated in the database
    - check: Source of the vessel data & informations
    - length_class: BLOOM size classes (in m)
    - excursion_id: Unique identifier for the excursion -- TO BE REMOVED IN API V3
    - position: Last known position geometry of the vessel
    - timestamp: Timestamp of the last known position of the vessel
    - heading: Last known heading of the vessel (in degrees).
    - speed: Last known speed of the vessel (in knots).
    - arrival_port_id: Identifier of the destination port of the excursion -- TO BE REMOVED IN API V3
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels__last_positions',
    tags=['mart', 'dim', 'vessel', 'last_position'],
    indexes=[
        {'columns': ['vessel_id'], 'type': 'btree', 'unique': True},
        {'columns': ['mmsi'], 'type': 'btree'},
        {'columns': ['ship_name'], 'type': 'btree'},
        {'columns': ['country_iso3'], 'type': 'btree'},
        {'columns': ['type'], 'type': 'btree'},
        {'columns': ['imo'], 'type': 'btree'},
        {'columns': ['cfr'], 'type': 'btree'},
        {'columns': ['type'], 'type': 'btree'},
        {'columns': ['length_class'], 'type': 'btree'},
        {'columns': ['external_marking'], 'type': 'btree'},
        {'columns': ['ircs'], 'type': 'btree'}
    ]
) }}

select
    last_raw_positions.vessel_id,
    last_raw_positions.position_mmsi__raw_last as mmsi,
    stg_vessels.dim_vessel_name as ship_name,
    stg_vessels.dim_vessel_details->>'width' as width,
    stg_vessels.dim_vessel_loa as length,
    stg_vessels.dim_vessel_flag as country_iso3,
    stg_vessels.dim_vessel_details->>'ship_type' as type,
    stg_vessels.dim_vessel_imo as imo,
    stg_vessels.dim_vessel_cfr as cfr,
    stg_vessels.dim_vessel_external_marking as external_marking,
    stg_vessels.dim_vessel_call_sign as ircs,
    stg_vessels.tracking_activated,
    stg_vessels.dim_vessel_status as tracking_status,
    NULL as home_port_id,
    stg_vessels.stg_dim_vessel_created_at as vessel_created_at,
    NULL as vessel_updated_at,
    stg_vessels.dim_vessel_source as check,
    dim_vessel_details->>'length_class' as length_class,
    NULL as excursion_id, -- TO BE REMOVED IN API V3
    last_raw_positions.position_point__raw_last as position,
    last_raw_positions.position_timestamp__raw_last as timestamp,
    last_raw_positions.position_heading__raw_last as heading,
    last_raw_positions.position_speed__raw_last as speed,
    NULL as arrival_port_id -- TO BE REMOVED IN API V3
from {{ ref("itm_vessel_last_raw_position") }} as last_raw_positions
left join {{ ref("stg_dim_vessels") }} as stg_vessels
    on last_raw_positions.vessel_id = stg_vessels.vessel_id
    and utils.safe_between(
        date_trunc('day', last_raw_positions.position_timestamp__raw_last)::date,
        date_trunc('day', stg_vessels.dim_vessel_start_date)::date,
        date_trunc('day', stg_vessels.dim_vessel_end_date)::date
    )
order by timestamp asc
