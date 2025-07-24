-- stg_spire_vessel_infos.sql
-- This file is used to create a staging table for vessel information from the Spire API.

/*
Détecter les changements dans la table Spire sur les données des navires associées à un MMSI
1. Passer les champs non agrégés hors MMSI en JSONB
2. Comparer current et lead
3. Si changement, pointer


*/

{{ config(
    enabled = false,
    schema = 'staging',
    materialized = 'table'
) }}

with 

spire_vessel_infos as (
    select 
        vessel_mmsi, -- Clé de jointure avec les tables de dimensions des vessels
        vessel_imo,
        vessel_name,
        vessel_callsign,
        vessel_flag,
        vessel_length,
        count(*) as nb_occurences, -- Nombre d'occurrences consécutives de la configuration pour chaque MMSI
        min(vessel_timestamp) as first_seen, -- Date de la première occurrence
        max(vessel_timestamp) as last_seen, -- Date de la dernière occurrence

    from {{ source('spire', 'spire_ais_data') }}
) ,

select * from ... 