-- mart_dim_ports.sql
/* This file is used to create a mart table for ports for API routes:
    - api/v1/port/{port_id} : Return one port by id
    - api/v1/ports: Return paginated ports

    Fields:
    - id: Unique identifier of the port
    - name: Name of the port
    - locode: Port's unique code
    - url: URL of the port's information
    - country_iso3: ISO3 code of the country where the port is located
    - latitude: Latitude of the port's location
    - longitude: Longitude of the port's location
    - geometry_point: Geometry point of the port's location
    - has_excursion: Boolean indicating if the port has excursions !! Caution: This field needs to be updated with itm_vessel_excursions
    - created_at: Creation timestamp of the port
    - updated_at: Last update timestamp of the port
*/

{{ config(
    schema='marts',
    materialized='table',
    alias='mart_dim_ports',
    tags=['mart', 'dim', 'port'],
    indexes=[
        {"columns": ["id"], "type": "btree", "unique": true},
        {"columns": ["locode"], "type": "btree", "unique": true},
        {"columns": ["name"], "type": "btree"},
        {"columns": ["geometry_point"], "type": "gist"},
        {"columns": ["has_excursion"], "type": "btree"}
    ]
) }}

with

ports_has_excursion as (
    select distinct port_id from (
        select distinct excursion_port_departure as port_id from {{ ref('itm_vessel_excursions') }}
        union all
        select distinct excursion_port_arrival as port_id from {{ ref('itm_vessel_excursions') }}
    ) as ports_with_excursion
),

itm_ports_updated as ( -- Consolider itm_dim_ports avec l'occurence d'excursions pour chaque port
    select 
        itm_ports.port_id,
        itm_ports.port_name,
        itm_ports.port_locode,
        itm_ports.port_url,
        itm_ports.port_country_iso3,
        itm_ports.port_latitude,
        itm_ports.port_longitude,
        itm_ports.port_geometry_point,
        -- Caution: This field needs to be updated with itm_vessel_excursions
        coalesce(phe.port_id is not NULL, FALSE) as port_has_excursion,
        itm_ports.port_created_at,
        itm_ports.port_updated_at
    from {{ ref('itm_dim_ports') }} itm_ports
    -- Join with ports_has_excursion to determine if the port has any excursions
    left join ports_has_excursion as phe
        on itm_ports.port_id = phe.port_id
)


-- Noms de champs correspondants à la route API
select
    port_id as id,
    port_name as name,
    port_locode as locode,
    port_url as url,
    port_country_iso3 as country_iso3,
    port_latitude as latitude,
    port_longitude as longitude,
    port_geometry_point as geometry_point,
    port_has_excursion as has_excursion,
    port_created_at as created_at,
    port_updated_at as updated_at
from itm_ports_updated
order by port_id