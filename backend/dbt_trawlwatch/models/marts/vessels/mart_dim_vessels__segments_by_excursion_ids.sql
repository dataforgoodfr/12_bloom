-- mart_dim_vessels__segments_by_excursion_ids.sql
/*
This file is used to create a mart table for segments for API routes :
    - api/v1/vessels/{vessel_id}/excursions/{excursion_id}/segments : Return segments associated to a specific excursion

    Fields:
        - excursion_id: Unique identifier of the excursion
        - vessel_id: Identifier of the vessel associated with the excursion
        - daysegments_date: Date of the segment
        - timestamp_start: Start timestamp of the segment
        - timestamp_end: End timestamp of the segment
        - segment_duration: Duration of the segment in seconds
        - average_speed: Average speed of the vessel during the segment
        - start_position: Position of the vessel at the start of the segment
        - end_position: Position of the vessel at the end of the segment
        - heading_at_start: Heading of the vessel at the start of the segment
        - heading_at_end: Heading of the vessel at the end of the segment
        - speed_at_start: Speed of the vessel at the start of the segment
        - speed_at_end: Speed of the vessel at the end of the segment
        - course_at_start: Course of the vessel at the start of the segment
        - course_at_end: Course of the vessel at the end of the segment
        - segment_type: Type of the segment (e.g., DEFAULT_AIS, AT_SEAS, FISHING)
        - in_amp_zone: Indicates if the segment is in a marine protected area (AMP)
        - in_territorial_waters: Indicates if the segment is in territorial waters
        - in_zones_with_no_fishing_rights: Indicates if the segment is in zones
        - created_at: Creation timestamp of the record
*/

{{
    config(
        schema='marts',
        materialized='table',
        alias='mart_dim_vessels__segments_by_excursion_ids',
        tags=['mart', 'dim', 'vessel', 'segment'],
        indexes=[
            {"columns": ["excursion_id"], "type": "btree"},
            {"columns": ["vessel_id"], "type": "btree"},
            {"columns": ["daysegments_date"], "type": "brin"},
            {"columns": ["timestamp_start"], "type": "brin"},
        ]
    )
}}

select 
    excursion_id,
    vessel_id,
    segment_ends_at_day as daysegments_date,
    segment_start_at as timestamp_start,
    segment_end_at as timestamp_end,
    segment_duration,
    segment_average_speed as average_speed,
    segment_position_start as start_position,
    segment_position_end as end_position,
    segment_heading_at_start as heading_at_start,
    segment_heading_at_end as heading_at_end,
    segment_speed_at_start as speed_at_start,
    segment_speed_at_end as speed_at_end,
    segment_course_at_start as course_at_start,
    segment_course_at_end as course_at_end,
    segment_type,
    case when is_in_amp_zone is NULL then false else is_in_amp_zone end as in_amp_zone,
    case when is_in_territorial_waters is NULL then false else is_in_territorial_waters end as in_territorial_waters,
    is_in_zone_with_no_fishing_rights as in_zones_with_no_fishing_rights,
    segment_created_at as created_at
from {{ ref('itm_vessel_segments') }} as itm_segments
order by vessel_id, daysegments_date, segment_start_at asc