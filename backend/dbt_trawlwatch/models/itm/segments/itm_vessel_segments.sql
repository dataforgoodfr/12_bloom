-- itm_vessel_segments.sql

/*
    1. Récupère les infos liées à position et position_prev dans itm_vessel_positions
    2. Détermine les droits de pêche en fonction de la position
    3. Crée les segments de navire entre ces deux positions
    4. Calcule la distance et la durée, ainsi que différentes métriques du segment

    ------ INFORMATIONS IMPORTANTES >>>

    La table est partitionnée et administrée par les fonctions :
    - itm.manage_itm_vessel_segments_partitions(), qui crée la table, les partitions initiales et les index
    - itm.ensure_itm_vessel_segments_future_partitions(), qui crée automatiquement les nouvelles partitions nécessaires

    [[[NE PAS UTILISER dbt run --full-refresh]]] sur ce modèle, car cela détruirait le partitionnement
    Pour une régénération complète : SELECT itm.manage_itm_vessel_segments_partitions(start_year,end_year, full_rebuild=true) (si changement de structure)
    puis dbt run --select itm_vessel_segments+ --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'

*/

{{ config(
    schema='itm',
    materialized='incremental',
    unique_key=['excursion_id', 'segment_end_at'],
    incremental_strategy = 'microbatch',
    event_time = 'segment_start_at',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-01-01',
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
    pos.position_id,
    pos.position_timestamp,
    pos.position_timestamp_day,
    pos.position_timestamp_month,

    pos.position_mmsi,
    pos.vessel_id,
    pos.position_latitude,
    pos.position_longitude,
    pos.position_rot,
    pos.position_speed,
    pos.position_course,
    pos.position_heading,

    pos.is_last_position, -- La position courante est-elle la dernière connue ?
    pos.is_first_position, -- La position courante est-elle la première connue ?
    pos.is_same_position, -- La position courante est-elle identique à la précédente ?

    pos.is_in_port, -- La position courante est-elle dans un port ?
    pos.is_same_port, -- La position courante est-elle dans le même port que la précédente ?
    pos.port_id, -- Le port dans lequel se trouve la position courante
    pos.port_exited, -- Le port dans lequel se trouvait la position précédente

    pos.position_status, -- Statut de la position courante

    coalesce(pos.position_id = exc.excursion_start_position_id, FALSE) as is_excursion_start, -- La position courante débute-t-elle une excursion ?
    coalesce(pos.position_id = exc.excursion_end_position_id, FALSE) as is_excursion_end, -- La position courante termine-t-elle une excursion ?

    pos.position_point, -- Position géographique de la position courante

    pos.position_itm_created_at, -- Date de création de la position dans la base de données (cette table)
    pos.nb_ais_messages,

    -- PREV
    pos.position_id_prev,

    -- METRICS
    --pos.time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
    --pos.time_diff_h, -- Temps écoulé entre la position courante et la précédente (  en heures)
    --pos.distance_m, -- Distance euclidienne entre la position courante et la précédente (en mètres)
    --distance_km, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
    --pos.distance_mi, -- Distance euclidienne entre la position courante et la précédente (en milles marins)

    exc.excursion_id,
    exc.excursion_start_position_timestamp,
    exc.excursion_end_position_timestamp,
    exc.excursion_status

    from (select * from {{ ref('itm_vessel_positions') }} ) as pos

    -- On conserve uniquement les positions correspondant à des excursions
    inner join ( select * from {{ ref('itm_vessel_excursions') }} ) as exc
        on pos.vessel_id = exc.vessel_id
        and pos.position_timestamp between exc.excursion_start_position_timestamp and exc.excursion_end_position_timestamp

    {{ MMSI_filter }}
),

vessel_positions_w_flag as (
    select
        vpos.*,
        vflag.vessel_flag--,
        --vflag_prev.vessel_flag as vessel_flag_prev
    from vessel_positions as vpos
    left join lateral ( -- Récupération du pavillon du navire à la position courante
        select f.vessel_flag
        from {{ ref('itm_vessel_flags') }} as f
        where f.vessel_id = vpos.vessel_id
            and utils.safe_between(vpos.position_timestamp, f.flag_start_at, f.flag_end_at)
        limit 1
    ) as vflag on TRUE
),

pos_w_zones as (
    select
        pos.vessel_id,
        pos.position_id,

        p_zones.zone_id,
        p_zones.zone_category,
        p_zones.zone_sub_category/*,

        prev_zones.zone_id as zone_id_prev,
        prev_zones.zone_category as zone_category_prev,
        prev_zones.zone_sub_category as zone_sub_category_prev*/

    from vessel_positions_w_flag as pos

    left join (select * from {{ ref('itm_vessel_positions_x_zones') }} ) as p_zones
        on (pos.vessel_id, pos.position_id) = (p_zones.vessel_id, p_zones.position_id)


),

--------<<< APPARTE pour le calcul des droits de pêche dans les zones maritimes
-- On embarque le moins possible de champs

get_fishing_beneficiaries as ( -- Charger les pavillons bénéficiaires de droits pêche dans les zones
    select
        zone_id, 
        zone_category,
        zone_sub_category,
        case -- Déterminer la famille de droits de pêche en fonction de la catégorie de zone
            when zone_category = 'amp' then 'amp'
            when zone_category = 'Territorial seas' then 'tw'
            when zone_category = 'Fishing coastal waters (6-12 NM)' then 'tw'
            when zone_category = 'Clipped territorial seas' then 'tw'
            else 'other'
        end as zone_rights_family,
        cast(beneficiaries as varchar[]) as zone_beneficiaries
    from {{ ref('itm_zone_fishing_rights') }}
    -- On ne conserve que les zones pour lesquelles des bénéficiaires sont explicitement désignés
    where beneficiaries is not NULL -- Les zones sans bénéficiaires ne contribuent ni à l'accumulation des droits, ni à l'évaluation des droits
),

vessel_fishing_rights_by_rights_family as ( -- Regrouper les droits de pêche par famille de droits selon les droits les plus favorables (UNION des droits)
    select
        pz.vessel_id,
        pz.position_id, 
        dz_ben.zone_rights_family,
        array_agg(pz.zone_id) filter (where pz.zone_id is not NULL) as family_zone_ids,
        array_agg(pz.zone_category) filter (where pz.zone_category is not NULL) as family_zone_categories,
        array_agg(pz.zone_sub_category) filter (where pz.zone_sub_category is not NULL) as family_zone_sub_categories,

        -- Concatène les flags distincts des zones de la famille de droits (permissif)
        utils.array_concat_uniq_agg(dz_ben.zone_beneficiaries) as family_zone_beneficiaries 

    from pos_w_zones as pz
    left join get_fishing_beneficiaries as dz_ben on pz.zone_id = dz_ben.zone_id
    -- On ne conserve que les positions en zone
	where pz.zone_id is not NULL
    group by pz.vessel_id, pz.position_id, dz_ben.zone_rights_family
),

vessel_fishing_rights_by_position as ( -- Calculer l'intersection des droits des différentes familles, donc les droits les moins favorables (ALL des droits)
    select
        vessel_id,
        position_id,
        utils.array_concat_uniq_agg(family_zone_ids) as zone_ids,
        utils.array_concat_uniq_agg(family_zone_categories) as zone_categories,
        utils.array_concat_uniq_agg(family_zone_sub_categories) as zone_sub_categories,
        
        -- Conserve uniquement les pavillons présents dans toutes les familles de droits (restrictif)
        utils.array_intersect_agg(cast(family_zone_beneficiaries as text[])) as flags_with_fishing_rights_on_position 
        
    from vessel_fishing_rights_by_rights_family
    group by vessel_id, position_id
),
-------->>>  FIN DE L'APPARTE pour la détermination des droits de pêche dans les zones maritimes

evaluate_fishing_rights_for_position as (
    select
        poswf.*,
        rights_by_pos.zone_ids,
        rights_by_pos.zone_categories,
        rights_by_pos.zone_sub_categories,
        rights_by_pos.flags_with_fishing_rights_on_position,
        {{ evaluate_fishing_rights('rights_by_pos.flags_with_fishing_rights_on_position', 'poswf.vessel_flag') }} as fishing_rights
    from vessel_positions_w_flag as poswf -- On ramène tous les champs écartés dans l'apparté
    left join vessel_fishing_rights_by_position as rights_by_pos -- On ajoute les champs compilés dans l'apparté
        on poswf.position_id = rights_by_pos.position_id
),

position_and_position_prev as ( --Récupération de la position précédente pour création du segment
    select 
        pos_w_r.*,
        --pos_w_r_prev.position_id as position_id_prev,
        pos_w_r_prev.position_timestamp as position_timestamp_prev,
        pos_w_r_prev.position_point as position_point_prev,
        pos_w_r_prev.vessel_flag as vessel_flag_prev,
        pos_w_r_prev.excursion_id as excursion_id_prev,
        pos_w_r_prev.excursion_start_position_timestamp as excursion_start_position_timestamp_prev,
        pos_w_r_prev.excursion_end_position_timestamp as excursion_end_position_timestamp_prev,
        pos_w_r_prev.excursion_status as excursion_status_prev,
        pos_w_r_prev.fishing_rights as fishing_rights_prev,
		pos_w_r_prev.flags_with_fishing_rights_on_position as flags_with_fishing_rights_on_position_prev,
        pos_w_r_prev.zone_ids as zone_ids_prev,
        pos_w_r_prev.zone_categories as zone_categories_prev,
        pos_w_r_prev.zone_sub_categories as zone_sub_categories_prev,
        pos_w_r_prev.position_speed as position_speed_prev,
        pos_w_r_prev.position_heading as position_heading_prev,
        pos_w_r_prev.position_course as position_course_prev,
        pos_w_r_prev.position_rot as position_rot_prev

    from evaluate_fishing_rights_for_position as pos_w_r
    left join evaluate_fishing_rights_for_position  as pos_w_r_prev
        on pos_w_r.position_id_prev = pos_w_r_prev.position_id
        and pos_w_r.excursion_id = pos_w_r_prev.excursion_id
    where pos_w_r.position_id_prev is not NULL -- On ne garde que les positions pour lesquelles on a une position précédente
),

segment_construction as (
    select
        concat(excursion_id, '_endat_', position_id ) as segment_id,
        excursion_id,
		excursion_id_prev,
		vessel_id,
        position_id,
        position_id_prev,
        position_timestamp,
        position_timestamp_prev,
        position_point,
        position_point_prev,
        --time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
        --time_diff_h, -- Temps écoulé entre la position courante et la précédente (  en heures)
        --distance_m, -- Distance euclidienne entre la position courante et la précédente (en mètres)
        --distance_km, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
        --distance_mi, -- Distance euclidienne entre la position courante et la précédente (en milles marins)
        position_course,
        position_course_prev,
        position_heading,
        position_heading_prev,
        position_speed,
        position_speed_prev,
        position_rot,
        position_rot_prev,
        is_last_position,
        case 
        when round(coalesce(extract(epoch from position_timestamp - position_timestamp_prev), 0)::numeric,0) between 0.1 and 1800 -- 30 minutes
            then 'AT_SEA'
            else 'DEFAULT_AIS' 
        end as segment_type,
        st_makeline(
            position_point_prev,
            position_point
        ) as segment_line,

        zone_ids,
        zone_categories,
        zone_sub_categories,

        zone_ids_prev,
        zone_categories_prev,
        zone_sub_categories_prev,

        utils.array_diff(zone_ids, zone_ids_prev) as zones_entered,
        utils.array_diff(zone_ids_prev, zone_ids) as zones_exited,
        utils.array_in_both(zone_ids, zone_ids_prev) as zones_crossed,

        'amp' = any(zone_categories) as is_in_amp_zone,
        'Territorial seas' = any(zone_categories) as is_in_territorial_waters,

        'amp' = any(zone_categories_prev) as was_in_amp_zone_prev,
        'Territorial seas' = any(zone_categories_prev) as was_in_territorial_waters_prev,

        vessel_flag,
		flags_with_fishing_rights_on_position,
		fishing_rights,
	
		vessel_flag_prev,
		flags_with_fishing_rights_on_position_prev,
		fishing_rights_prev,
        coalesce( fishing_rights = 'excluded', FALSE) as is_in_zone_with_no_fishing_rights,
		coalesce( fishing_rights_prev = 'excluded', FALSE) as was_in_zone_with_no_fishing_rights_prev

    from position_and_position_prev 
    where position_timestamp_prev is not null -- On ne garde que les positions pour lesquelles on a une position précédente
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
        round(coalesce(extract(epoch from position_timestamp - position_timestamp_prev), 0)::numeric,0)  as segment_duration_s,
        round(coalesce(extract(epoch from position_timestamp - position_timestamp_prev)/3600, 0)::numeric,4) as segment_duration_h,

         round(st_distance(position_point, position_point_prev)::numeric,1) as segment_distance_m,
         round((st_distance(position_point, position_point_prev)/1852)::numeric,1) as segment_distance_nm,

        position_course as segment_course_at_end,
        position_course_prev as segment_course_at_start,

        position_heading as segment_heading_at_end,
        position_heading_prev as segment_heading_at_start,

        position_speed as segment_speed_at_end,
        position_speed_prev as segment_speed_at_start,

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

        /* PATCH 01-08-2025 */
        coalesce(is_in_amp_zone and was_in_amp_zone_prev, FALSE) as is_in_amp_zone,
        coalesce(is_in_territorial_waters and was_in_territorial_waters_prev, FALSE) as is_in_territorial_waters,
        /* /PATCH 01-08-2025 */

        vessel_flag,
		flags_with_fishing_rights_on_position,
		fishing_rights,
	
		vessel_flag_prev,
		flags_with_fishing_rights_on_position_prev,
		fishing_rights_prev,
	
        is_in_zone_with_no_fishing_rights,
		was_in_zone_with_no_fishing_rights_prev,

        coalesce(is_last_position, FALSE) as is_last_vessel_segment,

        position_point as segment_position_end,
        position_point_prev as segment_position_start,
        segment_line,
        now() as segment_created_at -- Date de création du segment dans la base de données (cette table)
        
    from segment_construction
)

select 
    segment_id, -- Identifiant du segment
    excursion_id, -- Identifiant de l'excursion
    vessel_id, -- Identifiant du navire

    segment_start_at, -- TS de la position de début du segment
    segment_end_at, -- TS de la position de fin du segment

    segment_duration, -- Interval
    cast(segment_duration_s as bigint), -- Durée du segment en secondes
    segment_duration_h, -- Durée du segment en heures

    segment_course_at_end as segment_course, -- Route fond à la fin du segment en degrés
    segment_distance_m, -- Distance parcourue dans le segment en mètres (calculée entre les positions de début et de fin du segment)
    segment_distance_nm, -- Distance parcourue dans le segment en milles marins (calculée entre les positions de début et de fin du segment)

     -- Vitesse moyenne du segment en nœuds (calculée en faisant la moyenne des vitesses AIS disponibles)
    case  
            when segment_speed_at_end is not NULL and segment_speed_at_start is not NULL 
                then round((segment_speed_at_end + segment_speed_at_start)::numeric / 2.0, 1)
            when segment_speed_at_end is not NULL 
                then segment_speed_at_end
            when segment_speed_at_start is not NULL 
                then segment_speed_at_start
    end as segment_average_speed,

    -- Vitesse de la route fond en nœuds (calculée entre les positions de début et de fin du segment)
    round( ({{ dbt_utils.safe_divide('segment_distance_nm', 'segment_duration_h') }})::numeric, 1) as segment_course_speed, 

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
	
	----------- Droits de pêche
	vessel_flag_prev, --Pavillon de navire (début de segment)
	flags_with_fishing_rights_on_position_prev, -- Pavillons avec droits de pêche à la position (début de segment)
	fishing_rights_prev, -- Situation du navire au regard des droits de pêche (début de segment)
	
	vessel_flag, --Pavillon du navire (fin de segment)
	flags_with_fishing_rights_on_position, -- Pavillons avec droits de pêche à la position (fin de segment)
	fishing_rights, -- Situation du navire au regard des droits de pêche (fin de segment)

	is_in_zone_with_no_fishing_rights as ended_in_zone_with_no_fishing_rights, -- Le navire est-il, à la fin du segment, dans une zone pour laquelle il n'a pas de droit de pêche ?
	was_in_zone_with_no_fishing_rights_prev as started_in_zone_with_no_fishing_rights, -- Le navire était-il, au début du segment dans une zone pour laquelle il n'a pas de droit de pêche ?
	
	case -- Le navire est considéré comme présent dans une zone pour laquelle il n'a pas les droits de pêche uniquement s'il n'a les droits ni au début, ni à la fin du segment 
		when is_in_zone_with_no_fishing_rights and was_in_zone_with_no_fishing_rights_prev then true
		else false
	end as is_in_zone_with_no_fishing_rights,
	-----------/ Droits de pêche

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
