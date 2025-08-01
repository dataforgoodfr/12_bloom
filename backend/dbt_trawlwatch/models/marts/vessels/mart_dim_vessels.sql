-- mart_dim_vessels.sql
/* This file is used to create a mart table for vessels for API routes:
    - api/v1/vessels/{vessel_id} : Return one vessel by id
    - api/v1/vessels: Return paginated vessels

    Fields:
    - id: Unique identifier of the vessel
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
    - created_at: Timestamp when the vessel record was created in the database
    - updated_at: Timestamp when the vessel record was last updated in the database
    - check: Source of the vessel data & informations
    - length_class: BLOOM size classes (in m)
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_vessels',
    tags=['mart', 'dim', 'vessel'],
    indexes=[
        {"columns": ["id"], "type": "btree", "unique": true},
        {"columns": ["imo"], "type": "btree"},
        {"columns": ["cfr"], "type": "btree", "unique": true},
        {"columns": ["ircs"], "type": "btree"},
        {"columns": ["mmsi"], "type": "btree"},
        {"columns": ["ship_name"], "type": "btree"},
        {"columns": ["length_class"], "type": "btree"},
        {"columns": ["type"], "type": "btree"}
    ]
) }}

with 

-- Retrieve last record for each vessel and add last active MMSI
last_vessel_records as (
    select stg_vessels.*,
            stg_mmsi.dim_mmsi_mmsi,
    row_number() over (
                partition by stg_vessels.vessel_id
                order by stg_vessels.dim_vessel_start_date desc, stg_mmsi.dim_mmsi_start_date desc
            ) as rn
    from {{ ref("stg_dim_vessels" )}} as stg_vessels
    left join ( select * from {{ ref("stg_dim_mmsi") }} ) as stg_mmsi
        on stg_vessels.vessel_id = stg_mmsi.vessel_id
)

select
    vessel_id as id,
    dim_mmsi_mmsi as mmsi, 
    dim_vessel_name as ship_name,
    dim_vessel_details->>'width' as width,
    dim_vessel_loa as length,
    dim_vessel_flag as country_iso3,
    dim_vessel_details->>'ship_type' as type,
    dim_vessel_imo as imo,
    dim_vessel_cfr as cfr,
    dim_vessel_external_marking as external_marking,
    dim_vessel_call_sign as ircs,
    tracking_activated,
    dim_vessel_status as tracking_status,
    0 as home_port_id,
    stg_dim_vessel_created_at as created_at,
    NULL as updated_at,
    dim_vessel_source as check,
    dim_vessel_details->>'length_class' as length_class
from last_vessel_records
where rn = 1
order by dim_vessel_name asc
