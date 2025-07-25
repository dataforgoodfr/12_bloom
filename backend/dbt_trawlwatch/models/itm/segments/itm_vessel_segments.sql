-- itm_vessel_segments.sql

/*
1. Récupère les infos liées à position et position_prev dans itm_vessel_positions
2. Crée les segments de navire entre ces deux positions
3. Calcule la distance et la durée, ainsi que différentes métriques du segment


*/

{{ config(
    schema='itm',
    materialized='incremental',
    unique_key='segment_id',
    incremental_strategy = 'microbatch',
    event_time = 'segment_start_at',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-01-01',
    lookback = 3,
    tags=['itm', 'vessel', 'segments'],
    indexes=[
        {'columns': ['segment_id'], 'type': 'btree'},
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['segment_start_at'], 'type': 'btree'},
        {'columns': ['segment_start_position_id'], 'type': 'btree'},
        {'columns': ['segment_end_position_id'], 'type': 'btree'},
        {'columns': ['segment_end_at'], 'type': 'btree'},
        {'columns': ['segment_duration'], 'type': 'btree'},
        {'columns': ['segment_distance'], 'type': 'btree'},   
        {'columns': ['excursion_id'], 'type': 'btree'},
        {'columns': ['zone_ids'], 'type': 'btree'},
        {'columns': ['zone_categories'], 'type': 'btree'},
        {'columns': ['zone_sub_categories'], 'type': 'btree'},
        {'columns': ['segment_type'], 'type': 'btree'},
        {'columns': ['is_in_amp_zone'], 'type': 'btree'},
        {'columns': ['is_in_territorial_waters'], 'type': 'btree'},
        {'columns': ['is_in_zone_with_no_fishing_rights'], 'type': 'btree'},
        {'columns': ['is_last_vessel_segment'], 'type': 'btree'},
        {'columns': ['segment_position_start'], 'type': 'gist'},
        {'columns': ['segment_position_end'], 'type': 'gist'},
        {'columns': ['segment_line'], 'type': 'gist'}
    ],
    pre_hook="SELECT itm.ensure_itm_vessel_segments_future_partitions();"
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}

{% if mmsi_list | length > 0 %}
  {% set MMSI_filter = "where position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
  {% set MMSI_filter = "" %}
{% endif %}


with 

vessel_positions as (
    select
    position_id,
    position_timestamp,
    position_timestamp_day,
    position_timestamp_month,

    position_mmsi,
    itm_vessel_positions.vessel_id,
    position_latitude,
    position_longitude,
    position_rot,
    position_speed,
    position_course,
    position_heading,

    is_last_position, -- La position courante est-elle la dernière connue ?
    is_first_position, -- La position courante est-elle la première connue ?
    is_same_position, -- La position courante est-elle identique à la précédente ?

    is_in_port, -- La position courante est-elle dans un port ?
    is_same_port, -- La position courante est-elle dans le même port que la précédente ?
    port_id, -- Le port dans lequel se trouve la position courante
    port_exited, -- Le port dans lequel se trouvait la position précédente

    position_status, -- Statut de la position courante
    
    is_excursion_start, -- La position courante débute-t-elle une excursion ? 
    is_excursion_end, -- La position courante termine-t-elle une excursion ?

    position, -- Position géographique de la position courante
    
    position_itm_created_at, -- Date de création de la position dans la base de données (cette table)
    nb_ais_messages,

    -- PREV
    position_id_prev,
    position_timestamp_prev,
    position_status_prev, -- Statut de la position précédente
    position_prev, -- Position géographique de la position précédente

    -- METRICS
    time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
    time_diff_h, -- Temps écoulé entre la position courante et la précédente (  en heures)
    distance_m, -- Distance euclidienne entre la position courante et la précédente (en mètres)
    --distance_km, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
    distance_mi, -- Distance euclidienne entre la position courante et la précédente (en milles marins)

    itm_vessel_excursions.excursion_id as excursion_id,
    itm_vessel_excursions.excursion_start_position_timestamp,
    itm_vessel_excursions.excursion_end_position_timestamp,
    itm_vessel_excursions.excursion_status

    from (select * from {{ ref('itm_vessel_positions') }} ) itm_vessel_positions

    -- On conserve uniquement les positions correspondant à des excursions
    join ( select * from {{ ref('itm_vessel_excursions') }} ) itm_vessel_excursions
        on itm_vessel_positions.vessel_id = itm_vessel_excursions.vessel_id
        and itm_vessel_positions.position_timestamp between itm_vessel_excursions.excursion_start_position_timestamp and itm_vessel_excursions.excursion_end_position_timestamp

    {{ MMSI_filter }}
),

-------------[ A MODIFIER UNE FOIS L'HISTORISATION DES NAVIRES EN PLACE ] -------------------
get_vessel_flag as ( -- Extraction du pavillon du navire à partir de itm_dim_vessels 
    select
        vessel_id,
        country_iso3 as vessel_flag
    from {{ ref('stg_dim_vessels') }}
),

positions_w_vessel_flag as (
    select
        vp.*,
        vf.vessel_flag
    from vessel_positions vp
    left join get_vessel_flag vf
        on vp.vessel_id = vf.vessel_id
    -- Filtre sur les positions qui ont une position précédente comme point de départ du segment
    where position_id_prev is not null
),

-----------------------------------[ END (Voir aussi plus bas) ]-------------------------------

vessel_positions_w_lagged as ( -- Récupération des infos utiles sur la position précédente qui ne figurent pas dans itm_vessel_positions
    select
        p.*,

        lag(p.position_speed) over w as position_speed_prev,
        lag(p.position_rot) over w as position_rot_prev,
        lag(p.position_course) over w as position_course_prev,
        lag(p.position_heading) over w as position_heading_prev,

        lag(p.excursion_id) over w as excursion_id_prev,
        lag(p.excursion_start_position_timestamp) over w as excursion_start_position_timestamp_prev,
        lag(p.excursion_end_position_timestamp) over w as excursion_end_position_timestamp_prev,
        lag(p.excursion_status) over w as excursion_status_prev

    from positions_w_vessel_flag p
    window w as (
        partition by p.vessel_id
        order by p.position_timestamp asc
    )
),

vessel_positions_w_zones as (
    select
        p.*,

        p_zones.zone_id,
        p_zones.zone_category,
        p_zones.zone_sub_category,

        prev_zones.zone_id as zone_id_prev,
        prev_zones.zone_category as zone_category_prev,
        prev_zones.zone_sub_category as zone_sub_category_prev

    from vessel_positions_w_lagged p

    left join (select * from {{ ref('itm_vessel_positions_x_zones') }} ) p_zones
        on (p.vessel_id, p.position_id) = (p_zones.vessel_id, p_zones.position_id)
    left join (select * from {{ ref('itm_vessel_positions_x_zones') }} ) prev_zones
        on (p.vessel_id, p.position_id_prev) = (prev_zones.vessel_id, prev_zones.position_id)

),

--------<<< APPARTE pour le calcul des droits de pêche dans les zones maritimes

get_fishing_beneficiaries as ( -- Extraire les bénéficiaires de chaque zone à partir de itm_dim_zones
    select
        zone_id, 
        case 
            when zone_json_data->>'beneficiaries' is not null then string_to_array(zone_json_data->>'beneficiaries', ', ') -- Si un bénéficiaire spécifique est défini, on le récupère
            when zone_json_data->>'beneficiaries' is null and zone_category = 'amp' then null -- Si la zone est une AMP sans bénéficiaire spécifique, on considère que tous les pavillons sont bénéficiaires
            when zone_json_data->>'beneficiaries' is null and zone_category = 'Clipped territorial seas' then '{ "FR" }' -- Si la zone est une zone côtière, on considère que le pavillon français est bénéficiaire
            when zone_json_data->>'beneficiaries' is null and zone_category = 'Fishing coastal waters (6-12 NM)' then '{ "FR" }' -- Si la zone est une zone côtière, on considère que le pavillon français est bénéficiaire
            when zone_json_data->>'beneficiaries' is null and zone_category = 'Territorial seas' then '{ "FR" }'
            else null -- Dans tous les autres cas, on ne considère pas de bénéficiaires
        end as zone_beneficiaries
    from {{ ref('itm_dim_zones') }}
),

-------------[ A MODIFIER UNE FOIS L'HISTORISATION DES NAVIRES EN PLACE ] -------------------

fishing_rights as ( -- Evaluer les droits de pêche dans la zone à partir du pavillon et des bénéficiaires de la zone
    select
        pz.position_id,

        pz.zone_id,
        pz.zone_category,
        pz.zone_sub_category,
        pz.zone_id_prev,
        pz.zone_category_prev,
        pz.zone_sub_category_prev,

        dim_zone.zone_beneficiaries,
        dim_zone_prev.zone_beneficiaries as zone_beneficiaries_prev,

        -- Détermination des droits de pêche : si au moins une zone désigne le pavillon du navire comme bénéficiaire, alors le navire n'est pas dans une zone sans droit de pêche
        case 
            -- Si le pavillon du navire est dans la liste des bénéficiaires de la zone détectée à la position de début ou de fin :
            -- on considère qu'il est dans une zone avec droit de pêche
            when dim_zone.zone_beneficiaries is not null and vessel_flag = ANY(dim_zone.zone_beneficiaries) then false
            when dim_zone_prev.zone_beneficiaries is not null and vessel_flag = ANY(dim_zone_prev.zone_beneficiaries) then false


            -- Si aucun bénéficiaire n'est désigné, rien n'indique que le navire est dans une zone sans droit de pêche
            --A MODIFIER !!!
            when dim_zone.zone_beneficiaries is null and dim_zone_prev.zone_beneficiaries is null then false

            -- Si le navire ne fait pas partie des bénéficiaires explicitement désignés de la zone détectée, ni au début, ni à la fin du segment, il est dans une zone sans droit de pêche
            --A MODIFIER !!!
            when 
                dim_zone.zone_beneficiaries is not null and dim_zone_prev.zone_beneficiaries is not null 
                and vessel_flag != ANY(dim_zone.zone_beneficiaries) 
                and vessel_flag != ANY(dim_zone_prev.zone_beneficiaries)
            then true

            else false -- Dans tous les autres cas, on laisse le bénéfice du doute
        end as is_in_zone_with_no_fishing_rights

    from vessel_positions_w_zones pz
    left join get_fishing_beneficiaries dim_zone
        on pz.zone_id = dim_zone.zone_id
    left join get_fishing_beneficiaries dim_zone_prev
        on pz.zone_id_prev = dim_zone_prev.zone_id

),
-----------------------------------[ END ]-------------------------------

pre_segment_zones_agregation as (
    select
        position_id,

        array_agg(distinct fr.zone_id) as zone_ids,
        array_agg(distinct fr.zone_category) as zone_categories,
        array_agg(distinct fr.zone_sub_category) as zone_sub_categories,

        array_agg(distinct fr.zone_id_prev) as zone_ids_prev,
        array_agg(distinct fr.zone_category_prev) as zone_categories_prev,
        array_agg(distinct fr.zone_sub_category_prev) as zone_sub_categories_prev,

        ( select array_agg(elem) from (
            select unnest(array_agg(distinct fr.zone_id)) as elem
            except
            select unnest(array_agg(distinct fr.zone_id_prev)) as elem
        ) i) as zones_entered,

        ( select array_agg(elem) from (
            select unnest(array_agg(distinct fr.zone_id_prev)) as elem
            except
            select unnest(array_agg(distinct fr.zone_id)) as elem
        ) e) as zones_exited,

        ( select array_agg(elem) from (
            select unnest(array_agg(distinct fr.zone_id)) as elem
            intersect
            select unnest(array_agg(distinct fr.zone_id_prev)) as elem
        ) c) as zones_crossed, 

        bool_or(fr.zone_category = 'amp' or fr.zone_category_prev = 'amp') as is_in_amp_zone,
        bool_or(fr.zone_category = 'Territorial seas' or fr.zone_category_prev = 'Territorial seas') as is_in_territorial_waters,
        -- MODIER !!!
        bool_or(is_in_zone_with_no_fishing_rights) as is_in_zone_with_no_fishing_rights


    from fishing_rights fr
    group by position_id
),

-------->>> FIN APPARTE pour le calcul des droits de pêche dans les zones maritimes


segment_construction as (
    select 
        concat(p.excursion_id, '_s', lpad((ROW_NUMBER() OVER (PARTITION BY p.excursion_id ORDER BY p.position_timestamp))::text, 7, '0')) as segment_id,
        p.*, 
        case 
        when p.time_diff_s < 1800 -- 30 minutes
            then 'AT_SEA'
            else 'DEFAULT_AIS' 
        end as segment_type,
        vp_z.zone_ids,
        vp_z.zone_categories,
        vp_z.zone_sub_categories,
        vp_z.zone_ids_prev,
        vp_z.zone_categories_prev,
        vp_z.zone_sub_categories_prev,
        vp_z.zones_entered,
        vp_z.zones_exited,
        vp_z.zones_crossed,
        vp_z.is_in_amp_zone,
        vp_z.is_in_territorial_waters,
        vp_z.is_in_zone_with_no_fishing_rights,

        ST_MakeLine(
            p.position_prev,
            p.position
        ) as segment_line

    from vessel_positions_w_zones p
    left join pre_segment_zones_agregation vp_z
        on p.position_id = vp_z.position_id
),


segment_metrics as (
    select
        segment_id,
        excursion_id,
        vessel_id,

        position_timestamp_prev as segment_start_at,
        position_timestamp as segment_end_at,
        segment_type,

        (position_timestamp - position_timestamp_prev) as segment_duration,
        time_diff_s as segment_duration_s,
        time_diff_h as segment_duration_h,

        distance_m as segment_distance_m,
        distance_mi as segment_distance_nm,

        position_course as segment_course_at_end,
        position_course_prev as segment_course_at_start,

        position_heading as segment_heading_at_end,
        position_heading_prev as segment_heading_at_start,

        position_speed as segment_speed_at_end,
        position_speed_prev as segment_speed_at_start,
        case 
            when position_speed is not null and position_speed_prev is not null 
                then round((position_speed + position_speed_prev)::numeric / 2.0, 1)
            when position_speed is not null 
                then position_speed
            when position_speed_prev is not null 
                then position_speed_prev
            else null        
        end as segment_average_speed,
        round( ({{ dbt_utils.safe_divide('distance_mi', 'time_diff_h') }})::numeric, 1) as segment_course_speed,

        position_rot as segment_rot_at_end,
        position_rot_prev as segment_rot_at_start,
        

        zone_ids,
        zone_categories,
        zone_sub_categories,

        zone_ids_prev,
        zone_categories_prev,
        zone_sub_categories_prev,

        zones_entered,
        zones_exited,
        zones_crossed,

        is_in_amp_zone,
        is_in_territorial_waters,
        is_in_zone_with_no_fishing_rights,

        case when is_last_position then true else false end as is_last_vessel_segment,


        position as segment_position_start,
        position_prev as segment_position_end,
        segment_line,
        NOW() as segment_created_at -- Date de création du segment dans la base de données (cette table)
        
    from segment_construction vp
)


select 
    segment_id, -- Identifiant du segment
    excursion_id, -- Identifiant de l'excursion
    vessel_id, -- Identifiant du navire

    segment_start_at, -- TS de la position de début du segment
    segment_end_at, -- TS de la position de fin du segment

    segment_duration, -- Interval
    segment_duration_s::bigint, -- Durée du segment en secondes
    segment_duration_h, -- Durée du segment en heures

    segment_course_at_end as segment_course, -- Route fond à la fin du segment en degrés
    segment_distance_m, -- Distance parcourue dans le segment en mètres (calculée entre les positions de début et de fin du segment)
    segment_distance_nm, -- Distance parcourue dans le segment en milles marins (calculée entre les positions de début et de fin du segment)

    segment_average_speed, -- Vitesse moyenne du segment en nœuds (calculée en faisant la moyenne des vitesses AIS disponibles)
    segment_course_speed, -- Vitesse de la route fond en nœuds (calculée entre les positions de début et de fin du segment)

    segment_type, -- Type de segment (AT_SEA, DEFAULT_AIS)

    zone_ids, -- Identifiants des zones traversées à la position de fin du segment
    zone_categories, -- Catégories des zones traversées à la position de fin du segment
    zone_sub_categories, -- Sous-catégories des zones traversées à la position de fin du segment

    zone_ids_prev, -- Identifiants des zones traversées à la position de début du segment
    zone_categories_prev, -- Catégories des zones traversées à la position de début du segment
    zone_sub_categories_prev, -- Sous-catégories des zones traversées à la position de début du segment

    zones_entered, -- Différence entre zone_ids et zone_ids_prev : les zones dans lesquelles le navire est entré entre les 2 positions
    zones_exited, -- Différence entre zone_ids_prev et zone_ids : les zones dans lesquelles le navire est sorti entre les 2 positions
    zones_crossed, -- Intersection entre zone_ids et zone_ids_prev : les zones dans lesquelles le navire est resté entre les 2 positions

    is_in_amp_zone, -- Le navire est-il dans une zone AMP ?
    is_in_territorial_waters, -- Le navire est-il dans des eaux territoriales ?
    is_in_zone_with_no_fishing_rights, -- Le navire est-il dans une zone pour laquelle il n'a pas de droit de pêche ?

    is_last_vessel_segment, -- Le segment est-il le dernier connu pour le navire ?

    segment_speed_at_start, -- Vitesse AIS à la position de début du segment
    segment_speed_at_end, -- Vitesse AIS à la position de fin du segment

    segment_heading_at_start, -- Cap AIS à la position de début du segment
    segment_heading_at_end, -- Cap AIS à la position de fin du segment

    segment_course_at_end, -- Route fond à la position de fin du segment
    segment_course_at_start, -- Route fond à la position de début du segment

    segment_rot_at_start, -- Taux de rotation AIS à la position de début du segment 
    segment_rot_at_end, -- Taux de rotation AIS à la position de fin du segment

    to_char(segment_end_at, 'YYYYMM') as segment_ends_at_month, -- Mois de fin du segment (paritionnement)
    date_trunc('day', segment_end_at) as segment_ends_at_day, -- Jour de fin du segment pour faciliter l'extraction par jour
    now() as segment_created_at, -- Date de création du segment dans la base de données

    segment_position_start, -- Position géographique de début du segment, WGS84
    segment_position_end,  -- Position géographique de fin du segment, WGS84
    segment_line -- Ligne géographique du segment (entre les positions de début et de fin), WGS84

from segment_metrics
