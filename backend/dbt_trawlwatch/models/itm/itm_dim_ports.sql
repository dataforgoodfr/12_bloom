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
    SELECT
        port_id,
        ST_Transform(port_geometry_point, 6933) AS port_geom_proj6933
    FROM stg_ports
),


buffers_proj AS ( -- Buffer (radius en mètres indiqué par buffer_size_m) des ports, puis reprojection en WGS84
    SELECT
        port_id,
        coalesce({{ buffer_size_m }}::numeric, 0) as port_buffer_size_m,
        ST_Transform(
            ST_Buffer(port_geom_proj6933, coalesce({{ buffer_size_m }}::numeric, 0)),
            4326
        ) AS port_buffer_geom
    FROM ports_proj
),


voronoi AS ( -- Création des polygones de Voronoï
    -- Créer une géométrie multilinestring contenant tous les bords des polygones de Voronoï
    SELECT
        (ST_Dump(ST_VoronoiPolygons(ST_Collect(port_geometry_point)))).geom AS voronoi_geom
    FROM stg_ports
),


voronoi_joined AS ( -- Attribution de chaque polygone Voronoi au port auquel il correspond (intersection point-in-polygon)
    SELECT
        p.port_id,
        v.voronoi_geom
    FROM voronoi v
    JOIN stg_ports p
      ON ST_Intersects(v.voronoi_geom, p.port_geometry_point)
),


clipped_buffers AS ( -- Buffer final = intersection entre buffer fixe et polygone Voronoi
    SELECT
        b.port_id,
        b.port_buffer_size_m,
        ST_MakeValid(ST_Intersection(b.port_buffer_geom, v.voronoi_geom)) AS port_geometry_buffer
    FROM buffers_proj b
    LEFT JOIN voronoi_joined v ON b.port_id = v.port_id
),

join_it as (
    SELECT
        p.*,
        c.port_buffer_size_m,
        c.port_geometry_buffer
    FROM stg_ports p
    LEFT JOIN clipped_buffers c ON p.port_id = c.port_id
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