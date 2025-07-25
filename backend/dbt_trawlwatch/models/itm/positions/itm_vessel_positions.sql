-- itm_vessel_positions.sql
/*
    Ce modèle analyse les positions des navires, exclut les positions sans intérêt 
    (doublons, stationnement dans un port sauf entrée et sortie) 
    et ajoute des métriques liées à la fois à la position courante et à la position précédente.

    -> A étudier : 
    - Possibilité de streamer cette phase en mettant à jour par trigger dans stg_vessel_positions
     un champ has_been_analyzed pour toutes les positions correspondant à des excursions terminées (ou autre règle),
     pour ne matérialiser que les segments et les excursions ?
     - Possibilité de stocker matérialiser une vue qui sera moissonnée en batch par les tables de segments et d'excursions en aval ?
*/




{{ config(
    schema = 'itm',
    materialized = 'incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-05-01',
    lookback = 3,
    unique_key = ['position_id', 'position_timestamp_month'],
    pre_hook="SELECT itm.ensure_itm_vessel_positions_future_partitions();",
    enabled = true
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}

{% if mmsi_list | length > 0 %}
  {% set MMSI_filter = "where position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
  {% set MMSI_filter = "" %}
{% endif %}


with

----------------------------------- Récupération des dernières positions précédant le microbatch -------------------

previous_positions as ( -- Récupération d'1 ligne par vessel_id (la plus récente déjà stocké) pour le bon fonctionnement du LAG en microbatch
    select *
    from (
        select  
            position_id, 
            position_timestamp,
            position_mmsi, 
            vessel_id, 
            position_latitude, 
            position_longitude, 
            position_rot, 
            position_speed, 
            position_course, 
            position_heading,
            position,
            row_number() over (partition by vessel_id order by position_timestamp desc) as rn
        from {{ this }}
        {{ MMSI_filter }}
    ) t
    where rn = 1
),
raw_vessel_positions as ( -- Données remontées par le microbatch sur stg_vessel_positions
        select 
            position_id, 
            position_timestamp,
            position_mmsi, 
            vessel_id, 
            position_latitude, 
            position_longitude, 
            position_rot, 
            position_speed, 
            position_course, 
            position_heading,
            position,
            null::integer as rn
        from {{ ref('stg_vessel_positions') }} 
        
        {{ MMSI_filter }}
        

        union all          -- on ajoute la « dernière » ligne de chaque navire
        select * from previous_positions
        order by position_timestamp, vessel_id
),



---------------------------------------- Chargement des positions uniques des navires ---------------------------------------------
vessel_positions as (
    select 
        min(position_id) as position_id, -- On prend le min pour éviter les doublons stricts hors id
        position_timestamp,
        position_mmsi,
        vessel_id,
        position_latitude,
        position_longitude,
        position_rot,
        position_speed,
        position_course,
        position_heading,
        position,
        case when rn is not null then true else false end as is_anterior_position, -- Indique si la position est antérieure à la première position connue (pour le microbatch)
        count(*) as nb_ais_messages

     from raw_vessel_positions


     group by 
        position_timestamp, position_mmsi, vessel_id, position_latitude, position_longitude, 
        position_rot, position_speed, position_course, position_heading,
        position, rn

),

------------------------- Identification des positions remarquables + Suppression des doublons de positions ---------------------------------------------------
vessel_first_n_last_update as ( -- Récupération de la dernière position_timestamp connue pour chaque navire, déjà traitée dans itm_vessel_last_positions
    select vessel_id as vessel_id_flu, 
    first_position_timestamp, last_position_timestamp,
    first_position_id, last_position_id
    from {{ ref('itm_vessel_first_and_last_positions') }}
    order by vessel_id_flu
),

mark_first_and_last_positions as ( -- Marquage des positions de début et de fin de chaque navire
    select 
        *,
        -- Première position connue pour chaque navire 
        case when (position_timestamp,position_id) = (first_position_timestamp, first_position_id) then true else false end as is_first_position,
        -- Dernière position connue pour chaque navire
        case when (position_timestamp,position_id) = (last_position_timestamp, last_position_id) then true else false end as is_last_position 

    from vessel_positions
    left join vessel_first_n_last_update flu
        on vessel_positions.vessel_id = flu.vessel_id_flu
    where true
),


vessel_positions_w_previous as ( -- Récupération de la position précédente du point du vue temporel
    select 
        *,
        LAG(position_id) OVER w as position_id_prev,
        LAG(position_timestamp) OVER w as position_timestamp_prev,
        LAG(position) OVER w as position_prev
    from mark_first_and_last_positions
    WINDOW w AS (
        PARTITION BY vessel_id 
        ORDER BY position_timestamp
    )
),



vessel_positions_flag_it as ( -- Identification des positions identiques à la précédente
    select 
        *,
        
        -- La position courante est-elle identique (temporellement et géographiquement) à la position précédente ?
        case 
            when position_timestamp_prev is not null -- La position précédente existe
            and position_timestamp = position_timestamp_prev -- Le timestamp est identique
            and ST_Equals(position, position_prev) -- La position géographique est identique
        then true else false end as is_same_position

    from vessel_positions_w_previous
    left join vessel_first_n_last_update flu
        on vessel_positions_w_previous.vessel_id = flu.vessel_id_flu
),

drop_same_position as ( -- Supprimer les positions identiques à la précédente
    select * from vessel_positions_flag_it
    where  is_same_position = false or is_first_position or is_last_position -- On garde les positions identiques à la précédente si elles sont la première ou la dernière position connue
    order by position_timestamp, vessel_id
),

----------------------------------- Croisement spatial avec les périmètres de ports -------------------------------------

ports as ( -- Chargement des ports avec buffer
    select 
        port_id,
        port_geometry_point,
        port_buffer_size_m, -- Va permettre un prétraitement rapide des ports candidats avant le ST_Intersects (avec ST_DWinthin & radius)
        port_geometry_buffer
    from {{ ref('itm_dim_ports') }}
),

positions_x_ports as ( -- Croisement spatial des positions courantes des navires avec les ports
    select
        vp.*,
        case when p.port_id is not null then true else false end as is_in_port, -- La position courante est-elle dans un port ?
        p.port_id,
        case
            when p.port_id is null then 'at_sea' -- Si le navire navigue à au moins 2 nœuds, on considère qu'il est en mer
            when p.port_id is not null and vp.position_speed < 2.0 then 'in_port' -- Si le navire est détecté dans un port à une vitesse inférieure à 2 nœuds, on considère qu'il est stationné dans le port
            when p.port_id is not null and vp.position_speed >= 2.0 then 'transiting_in_port_area' -- Si le navire est détecté dans un port à une vitesse supérieure à 2 nœuds, on considère qu'il est en mer
            else 'unknown' -- Si aucune condition n'est remplie, on considère que la position est inconnue
        end as position_status -- Statut de la position du navire

    from drop_same_position vp
    left join ports p 
        on vp.position && p.port_geometry_buffer
        and ST_DWithin( -- Prétraitement sur BBox avec radius
                st_transform(vp.position, 3857), -- Passage en unités métriques
                st_transform(p.port_geometry_point, 3857), -- Passage en unités métriques
                p.port_buffer_size_m
            ) 
        and ST_Intersects(vp.position, p.port_geometry_buffer) -- Intersection avec le buffer Voronoi des ports
),

-- Ne conserver que les positions pour lesquelles le bateau n'est pas stationné dans le même port que la position précédente

lag_position_status as ( -- Comparer la situation de la position courante avec la précédente du point de vue du port
    select 
        *,
        LAG(is_in_port) OVER w as is_in_port_prev,
        LAG(port_id) OVER w as port_id_prev,
        LAG(position_status) OVER w as position_status_prev
    from positions_x_ports
    WINDOW w AS (PARTITION BY vessel_id ORDER BY position_timestamp)
),

position_of_interest as ( -- Conserver uniquement les positions qui ont un intérêt pour l'analyse
    select 
        *,
        case when is_in_port and is_in_port_prev and port_id = port_id_prev then true else false end as is_same_port
    from lag_position_status
    where 
        is_first_position = true -- On conserve la première position connue
        or is_last_position = true -- On conserve la dernière position connue
        or position_status in ('unknown','at_sea','transiting_in_port_area') -- On conserve les positions pour lesquelles le navire est en mouvement ou quand le statut est inconnu
        or position_status_prev in ('at_sea','transiting_in_port_area') -- On conserve les positions pour lesquelles le navire était précédemment en mouvement
        or position_status_prev != position_status -- On conserve les positions pour lesquelles le navire n'est pas en mouvement, mais a changé de statut de position
        or ((position_status = 'in_port' and position_status_prev = 'in_port') and not port_id = port_id_prev ) -- On conserve les positions pour lesquelles le navire est toujours stationné, mais dans un port différent de la position précédente
        or is_first_position or is_last_position -- On conserve la première et la dernière position connue
),

------------------------- Définition des débuts et fins d'excursions à partir des positions des navires -------------------------------------

excursions_define as ( -- Définition des excursions à partir des évolutions de la position du point de vue du port
    -- Une excursion débute lorsque le navire sort du périmètre portuaire dans lequel il était stationné ou 
    -- Une excursion se termine lorsqu'un navire situé dans un périmètre portuaire voit sa vitesse tomber sous 2 nœuds
	select 
		*,
		-- La position courante débute-t-elle une excursion ?
        case 
            when is_first_position and position_status != 'in_port' then true -- La première position connue pour un navire est, s'il n'est pas au port, considérée comme le début d'une excursion
            when is_first_position and position_status = 'in_port' then false -- La première position connue pour un navire n'est pas, s'il est au port, considérée comme le début d'une excursion
            --when is_last_position then false -- VRAIMENT ??? La dernière position connue pour un navire n'est pas considérée comme le début d'une excursion
            when position_status_prev = 'in_port' and position_status != 'in_port' then true -- Le bateau était précédemment stationné dans un port et a changé de statut
            when position_status_prev = 'in_port' and position_status = 'in_port' and not is_same_port then true -- Le bateau était déjà précédemment stationné dans un port mais a changé de port
            else false
        end as is_excursion_start, 
        
        -- La position courante termine-t-elle une excursion ?
        case 
            when position_status = 'in_port' and position_status_prev != 'in_port' then true -- Le bateau est stationné dans un port, ce n'était pas le cas précédemment
            when position_status = 'in_port' and position_status_prev = 'in_port' and not is_same_port then true -- Le bateau était déjà précédemment stationné dans un port mais a changé de port  
            else false
        end as is_excursion_end
	from position_of_interest
),

-------------------------------------------- Cacul de métriques basiques sur les positions ---------------------------------------------

diff_between_positions as ( -- Calcul des différences entre la position courante et la précédente
    select
        *,  
        EXTRACT(EPOCH FROM (position_timestamp - position_timestamp_prev)) as time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
        (ST_Distance(st_transform(position, 3857), st_transform(position_prev, 3857))) as distance_m -- Distance euclidienne entre la position courante et la précédente (en mètres)
    from excursions_define
),

vessel_positions_w_diff_convert as (
    select 
        *,
        round((time_diff_s / 3600), 3) as time_diff_h,
        (distance_m / 1000) as distance_km,
        (distance_m / 1852) as distance_mi

    from diff_between_positions
)

---------------------------------------------- Sortie finale ------------
select
    l.position_id,
    l.position_id_prev,
    l.position_timestamp,
    l.position_timestamp_prev,
    CAST(date_trunc('day', l.position_timestamp) AS date) AS position_timestamp_day,
    to_char(l.position_timestamp, 'YYYYMM') AS position_timestamp_month,

    l.position_mmsi,
    l.vessel_id,
    l.position_latitude,
    l.position_longitude,
    l.position_rot,
    l.position_speed,
    l.position_course,
    l.position_heading,

    l.is_last_position, -- La position courante est-elle la dernière connue ?
    l.is_first_position, -- La position courante est-elle la première connue ?
    l.is_same_position, -- La position courante est-elle identique à la précédente ?



    l.is_in_port, -- La position courante est-elle dans un port ?
    l.is_same_port, -- La position courante est-elle dans le même port que la précédente ?
    l.port_id, -- Le port dans lequel se trouve la position courante
    l.port_id_prev as port_exited, -- Le port dans lequel se trouvait la position précédente

    l.position_status, -- Statut de la position courante
    l.position_status_prev, -- Statut de la position précédente
    l.is_excursion_start, -- La position courante débute-t-elle une excursion ? 
    l.is_excursion_end, -- La position courante termine-t-elle une excursion ?

    l.time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
    l.time_diff_h, -- Temps écoulé entre la position courante et la précédente (  en heures)
    l.distance_m, -- Distance euclidienne entre la position courante et la précédente (en mètres)
    l.distance_km, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
    l.distance_mi, -- Distance euclidienne entre la position courante et la précédente (en milles marins)

    l.position, -- Position géographique de la position courante
    l.position_prev, -- Position géographique de la position précédente
    l.nb_ais_messages, -- Nombre de messages AIS reçus pour cette position
    now() as position_itm_created_at -- Date de création de la position dans la base de données (cette table)

from vessel_positions_w_diff_convert l

where true 
    --and existing_positions.position_id is null -- On ne garde que les nouvelles positions
    and l.is_anterior_position = false -- On ne garde pas la position antérieure ajoutée seulement pour les LAG dans le microbatch
    and l.is_same_position = false -- Exclure les positions identiques à la précédente
order by l.position_timestamp, l.vessel_id