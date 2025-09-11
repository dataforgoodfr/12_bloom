-- mart_metrics__detailed_visits.sql
/*
This file is used to create a mart table for zones visited or vessels visiting zones for API routes :
    - api/v1/metrics/zones/{zone-id}/visiting-time-by-vessel : Return paginated list of vessels that visited a zone with total duration between dates
    - api/v1/metrics/vessels/time-by-zone : Return paginated list of zones visited by one or more vessels with total duration between dates (by category or subcategory)
    
    Fields:
    - day_date: Day of the count
    - zone_id: Identifier of the zone visited
    - category: Category of the zone (e.g., 'amp', 'Territorial seas', etc.)
    - sub_category: Sub-category of the zone
    - name: Name of the zone
    - zone_created_at: Creation timestamp of the zone record
    - centroid: Geographic centroid of the zone
    - vessel_id: Identifier of the vessel that visited the zone
    - mmsi: MMSI number of the vessel
    - ship_name: Name of the vessel
    - length: Length of the vessel
    - country_iso3: ISO3 code of the country of the vessel
    - type: Type of the vessel
    - imo: IMO number of the vessel
    - ircs: International Radio Call Sign of the vessel
    - vessel_created_at: Creation timestamp of the vessel record
    - zone_visiting_duration: Total time spent by the vessel in the zone
    - created_at: Creation timestamp of the record
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_metrics__detailed_visits',
    tags=['mart', 'metrics', 'zone', 'vessel'],
    indexes=[
        {"columns": ["day_date"], "type": "btree"},
        {"columns": ["zone_id"], "type": "btree"},
        {"columns": ["vessel_id"], "type": "btree"},
        {"columns": ["category"], "type": "btree"},
        {"columns": ["sub_category"], "type": "btree"},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["centroid"], "type": "gist"},
        {"columns": ["zone_visiting_duration"], "type": "btree"}
    ]
) }}

with 

zones_data as (
    select 
        segment_ends_at_day as day_date,
        vessel_id,
        unnest(zones_crossed) as zone_id,
        segment_duration
    from {{ ref('itm_vessel_segments') }}
    where zones_crossed is not null
)

select 
    day_date,
    zd.zone_id,
    zones.zone_name as name,
    zones.zone_category as category,
    zones.zone_sub_category as sub_category,
    zones.zone_created_at as zone_created_at,
    zones.zone_centroid as centroid,
    vessels.vessel_id as vessel_id,
    mmsi.dim_mmsi_mmsi as mmsi,
    vessels.dim_vessel_name as ship_name,
    vessels.dim_vessel_loa as length,
    vessels.dim_vessel_flag as country_iso3,
    vessels.dim_vessel_details->>'type' as type,
    vessels.dim_vessel_imo as imo,
    vessels.dim_vessel_call_sign as ircs,
    vessels.stg_dim_vessel_created_at as vessel_created_at,
    sum(segment_duration) as zone_visiting_duration,
    now() as created_at
from zones_data as zd
left join {{ ref('stg_dim_zones') }} as zones
on zones.zone_id::varchar = zd.zone_id
left join {{ ref('stg_dim_vessels') }} as vessels
on vessels.vessel_id = zd.vessel_id
    and utils.safe_between(day_date, vessels.dim_vessel_start_date, vessels.dim_vessel_end_date)
left join {{ ref('stg_dim_mmsi')}} as mmsi
on mmsi.vessel_id = vessels.vessel_id
    and utils.safe_between(day_date, mmsi.dim_mmsi_start_date, mmsi.dim_mmsi_end_date)
group by day_date, 
    zd.zone_id, 
    zones.zone_name, 
    zones.zone_category, 
    zones.zone_sub_category, 
    zones.zone_created_at, 
    zones.zone_centroid,
    vessels.vessel_id,
    mmsi.dim_mmsi_mmsi,
    vessels.dim_vessel_name,
    vessels.dim_vessel_loa,
    vessels.dim_vessel_flag,
    vessels.dim_vessel_details->>'type',
    vessels.dim_vessel_imo,
    vessels.dim_vessel_call_sign,
    vessels.stg_dim_vessel_created_at
order by zd.zone_id, vessels.vessel_id, day_date
