-- itm_dim_ports.sql
-- This file is used to create a staging table for Ports with Voronoï buffer established on the buffer_size_m parameter.
{{ config(
    schema='itm',
    tags=['seed','dim', 'ports'],
    materialized='table',
    unique_key='locode',
    indexes=[
        {"columns": ["port_id"], "type": "btree", "unique": true},
        {"columns": ["port_locode"], "type": "btree", "unique": true},
        {"columns": ["port_name"], "type": "btree"},
        {"columns": ["port_country_iso3"], "type": "btree"},
        {"columns": ["port_geometry_point"], "type": "gist"},
        {"columns": ["port_geometry_buffer"], "type": "gist"}
    ]
) }}

{% set buffer_size_m = 3000 %}

with 

stg_ports as (
    select * from {{ ref('seed_dim_ports') }}
),

ports_proj AS ( -- Projection en EPSG:6933 (Equal Area, adapté pour distances en m)
    select
        port_id,
        st_transform(port_geometry_point, 6933) AS port_geom_proj6933
    FROM stg_ports
),

buffers_proj AS ( -- Buffer (radius en mètres indiqué par buffer_size_m) des ports, puis reprojection en WGS84
    select
        port_id,
        coalesce({{ buffer_size_m }}::numeric, 0) as port_buffer_size_m,
        st_transform(
            st_buffer(port_geom_proj6933, coalesce({{ buffer_size_m }}::numeric, 0)),
            4326
        ) AS port_buffer_geom
    FROM ports_proj
),

voronoi AS ( -- Création des polygones de Voronoï
    -- Créer une géométrie multilinestring contenant tous les bords des polygones de Voronoï
    select (st_dump( st_voronoipolygons(st_collect(port_geometry_point)))).geom AS voronoi_geom
    from stg_ports
),

voronoi_joined AS ( -- Attribution de chaque polygone Voronoi au port auquel il correspond (intersection point-in-polygon)
    select
        ports.port_id,
        vor.voronoi_geom
    from voronoi as vor
    inner join stg_ports as ports
      on st_intersects(vor.voronoi_geom, ports.port_geometry_point)
),

clipped_buffers AS ( -- Buffer final = intersection entre buffer fixe et polygone Voronoi
    select
        buff.port_id,
        buff.port_buffer_size_m,
        st_makevalid(st_intersection(buff.port_buffer_geom, vor.voronoi_geom)) AS port_geometry_buffer
    from buffers_proj as buff
    LEFT JOIN voronoi_joined as vor ON buff.port_id = vor.port_id
),

join_it as (
    select
        ports.*,
        clip.port_buffer_size_m,
        clip.port_geometry_buffer
    from stg_ports as ports
    left join clipped_buffers as clip 
        ON ports.port_id = clip.port_id
)

select 
    port_id,
    port_name,
    port_country_iso3,
    port_locode,
    port_has_excursion,
    port_latitude,
    port_longitude,
    port_url,
    port_geometry_point,
    port_created_at,
    port_updated_at,
    port_buffer_size_m,
    port_geometry_buffer
from join_it
order by port_id
