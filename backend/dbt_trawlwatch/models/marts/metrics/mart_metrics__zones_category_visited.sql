-- mart_metrics__zones_category_visited.sql
/*
This file is used to create a mart table for zones category visited for API routes :
    - api/v1/metrics/vessels/activity : Return vessels with their total time in each zone category duration between dates

    Fields:
    - day_date: Day of the count
    - vessel_id: Identifier of the vessel that visited the zone
    - mmsi: MMSI number of the vessel
    - ship_name: Name of the vessel
    - length: Length of the vessel
    - country_iso3: ISO3 code of the country of the vessel
    - type: Type of the vessel
    - imo: IMO number of the vessel
    - ircs: International Radio Call Sign of the vessel
    - time_in_amp_zone: Total time spent in 'amp'
    - time_in_territorial_waters: Total time spent in 'Territorial waters'
    - time_in_zone_with_no_fishing_rights: Total time spent in 'Zones with no fishing rights'  
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__zones_category_visited',
    tags=['mart', 'metrics', 'zone', 'vessel'],
    indexes=[
        {"columns": ["day_date"], "type": "btree"},
        {"columns": ["vessel_id"], "type": "btree"},
        {"columns": ["time_in_amp_zone"], "type": "btree"},
        {"columns": ["time_in_territorial_waters"], "type": "btree"},
        {"columns": ["time_in_zone_with_no_fishing_rights"], "type": "btree"}
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
    daysegments_date as day_date,
    vessels.vessel_id as vessel_id,
    dim_mmsi_mmsi as mmsi, 
    dim_vessel_name as ship_name,
    dim_vessel_details->>'width' as width,
    dim_vessel_loa as length,
    dim_vessel_flag as country_iso3,
    dim_vessel_details->>'ship_type' as type,
    dim_vessel_imo as imo,
    dim_vessel_cfr as cfr,
    dim_vessel_call_sign as ircs,
    sum(time_in_amp_zone) as time_in_amp_zone,
    sum(time_in_territorial_waters) as time_in_territorial_waters,
    sum(time_in_zone_with_no_fishing_rights) as time_in_zone_with_no_fishing_rights,
    now() as created_at
from {{ ref('itm_vessel_segments_by_date') }} as segments
left join last_vessel_records as vessels
on vessels.vessel_id = segments.vessel_id
where segments.segment_type = 'AT_SEA'
group by day_date, vessels.vessel_id, dim_mmsi_mmsi, dim_vessel_name, dim_vessel_details, dim_vessel_loa, dim_vessel_flag, dim_vessel_imo, dim_vessel_cfr, dim_vessel_call_sign
order by vessels.vessel_id, day_date


