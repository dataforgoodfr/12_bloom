-- itm_vessel_positions.sql
/*
    Ce modèle analyse les positions des navires, exclut les positions sans intérêt 
    (doublons, stationnement dans un port sauf entrée et sortie) 
    et ajoute des métriques liées à la fois à la position courante et à la position précédente.
    Fonctionnant en microbatch, il a besoin de charger la dernière position avant le microbatch pour fonctionner correctement (CTE previous_position).

    ------ INFORMATIONS IMPORTANTES >>>

    La table est partitionnée et administrée par les fonctions :
    - itm.manage_itm_vessel_positions_partitions(), qui crée la table, les partitions initiales et les index
    - itm.ensure_itm_vessel_positions_future_partitions(), qui crée automatiquement les nouvelles partitions nécessaires

    [[[NE PAS UTILISER dbt run --full-refresh]]] sur ce modèle, car cela détruirait le partitionnement
    Pour une régénération complète : SELECT itm.manage_itm_vessel_positions_partitions(start_year,end_year, full_rebuild=true) (si changement de structure)
    puis dbt run --select itm_vessel_positions+ --event-time-start "2024-05-01" --event-time-end "<<<remplacer par : today + 1 day>>>" --vars '{default_microbatch_size: "day"}'
*/

{{ config(
    enabled = true,
    schema = 'itm',
    materialized = 'incremental',
    incremental_strategy = 'microbatch',
    event_time = 'position_timestamp',
    batch_size = var('default_microbatch_size', 'hour'),
    begin = '2024-05-01',
    unique_key = ['position_id', 'position_timestamp_month'],
    pre_hook="SELECT itm.ensure_itm_vessel_positions_future_partitions();",
    post_hook="ANALYZE {{ this }};"
    
) }}

-- Gestion des run à partir d'une liste de MMSI
{% set mmsi_list = var('default_mmsi_list', []) %}
{% if mmsi_list | length > 0 %}
  {% set MMSI_filter = "and position_mmsi in (" ~ mmsi_list | join(',') ~ ")" %}
{% else %}
  {% set MMSI_filter = "" %}
{% endif %}


with

----------------------------------- Récupération des dernières positions précédant le microbatch -------------------
/*previous_positions as ( -- Récupération d'1 ligne par vessel_id (la plus récente déjà stocké) pour le bon fonctionnement du LAG en microbatch
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
            position_point,
            row_number() over (partition by vessel_id order by position_timestamp desc) as rn
        from {{ this }}
        {{ MMSI_filter }}
    ) as previous_entries
    where rn = 1
),*/

 -- noqa
----------------------------------- Chargement des positions stagées des navires -----------------------------------
raw_vessel_positions_load as ( -- Données remontées par le microbatch sur stg_vessel_positions
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
            position_point,
            cast(NULL as boolean) as rn
        from {{ ref('stg_vessel_positions') }} 
        where TRUE
            and vessel_id not like 'UNKNOWN_MMSI=%'
        {{ MMSI_filter }}
    
),

{% if is_incremental() %}
get_start_batch as ( -- Récupération de la date de début du microbatch
    select min(position_timestamp) as start_batch
    from raw_vessel_positions_load
),

{% endif %}

previous_positions AS (
  SELECT DISTINCT ON (this.vessel_id)
         this.position_id,
         this.position_timestamp,
         this.position_mmsi,
         this.vessel_id,
         this.position_latitude,
         this.position_longitude,
         this.position_rot,
         this.position_speed,
         this.position_course,
         this.position_heading,
         this.position_point,
         TRUE AS rn               
  FROM {{ this }} as this
  inner join (
    SELECT vessel_id as vessel_id_ld, max(position_timestamp_day) as ts_day_ld from {{ this }} 
    {% if is_incremental() %}
    where position_timestamp < (select start_batch from get_start_batch)
    {% endif %}
    group by vessel_id
  ) ld 
	on (this.vessel_id, this.position_timestamp_day) = (ld.vessel_id_ld, ld.ts_day_ld)
  {{ MMSI_filter }}
  ORDER BY this.vessel_id, this.position_timestamp DESC
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
            position_point,
            cast(NULL as boolean) as rn
        from raw_vessel_positions_load
        
        {{ MMSI_filter }}
        
        union all          -- on ajoute la « dernière » ligne de chaque navire
        select * from previous_positions
        order by position_timestamp, vessel_id
),
---------------------------------------- Chargement des positions uniques des navires ---------------------------------------------
/*vessel_positions as (
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
        position_point,
        coalesce(rn is not NULL, FALSE) as is_anterior_position, -- Indique si la position est antérieure à la première position connue (pour le microbatch)
        count(*) as nb_ais_messages

     from raw_vessel_positions
     group by 
        position_timestamp, position_mmsi, vessel_id, position_latitude, position_longitude, 
        position_rot, position_speed, position_course, position_heading,
        position_point, rn

),*/

vessel_positions AS (-- Supprimer les doublons de positions résiduels éventuels
  SELECT DISTINCT ON (vessel_id,position_timestamp)
         vessel_id,
         position_timestamp,
         position_id,
         position_mmsi,
         
         position_latitude,
         position_longitude,
         position_rot,
         position_speed,
         position_course,
         position_heading,
         position_point,
         (rn IS NOT NULL) AS is_anterior_position,
         1                AS nb_ais_messages
  FROM raw_vessel_positions
  ORDER BY 1,2       -- n’importe quel ORDER BY couvrant les colonnes de DISTINCT
),

------------------------- Identification des positions remarquables + Suppression des doublons de positions ---------------------------------------------------
vessel_first_n_last_update as ( -- Récupération de la dernière position_timestamp connue pour chaque navire, déjà traitée dans itm_vessel_last_positions
    select
        vessel_id as vessel_id_flu, 
        first_position_timestamp, last_position_timestamp,
        first_position_id, last_position_id
    from {{ ref('itm_vessel_first_and_last_positions') }}
    order by vessel_id_flu
),

mark_first_and_last_positions as ( -- Marquage des positions de début et de fin de chaque navire
    select 
        pos.*,
        -- Première position connue pour chaque navire 
        coalesce( (pos.position_timestamp,pos.position_id) = (flu.first_position_timestamp, flu.first_position_id), false) as is_first_position,
        -- Dernière position connue pour chaque navire
        coalesce( (pos.position_timestamp,pos.position_id) = (flu.last_position_timestamp, flu.last_position_id), false) as is_last_position 

    from vessel_positions as pos
    left join vessel_first_n_last_update as flu
        on pos.vessel_id = flu.vessel_id_flu
    where TRUE
),

vessel_positions_w_previous as ( -- Récupération de la position précédente du point du vue temporel
    select 
        *,
        lag(position_id) over w as position_id_prev,
        lag(position_timestamp) over w as position_timestamp_prev,
        lag(position_point) over w as position_point_prev
    from mark_first_and_last_positions
    window w as (
        partition by vessel_id 
        order by position_timestamp
    )
),

vessel_positions_flag_it as ( -- Identification des positions identiques à la précédente
    select 
        posp.*,
        
        -- La position courante est-elle identique (temporellement et géographiquement) à la position précédente ?
        coalesce(
            (posp.position_timestamp_prev is not NULL -- La position précédente existe
            and posp.position_timestamp = posp.position_timestamp_prev -- Le timestamp est identique
            and posp.position_point = posp.position_point_prev), -- La position géographique est identique
            FALSE) as is_same_position

    from vessel_positions_w_previous as posp
),

drop_same_position as ( -- Supprimer les positions identiques à la précédente
    select * 
    from vessel_positions_flag_it
    -- On garde les positions identiques à la précédente si elles sont la première ou la dernière position connue
    where is_same_position = FALSE or is_first_position or is_last_position 
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
        pos.*,
        coalesce(ports.port_id is not NULL, FALSE) as is_in_port, -- La position courante est-elle dans un port ?
        ports.port_id,
        case
            -- Si le navire navigue à au moins 2 nœuds, on considère qu'il est en mer
            when ports.port_id is NULL then 'at_sea' 
            -- Si le navire est détecté dans un port à une vitesse inférieure à 2 nœuds, on considère qu'il est stationné dans le port
            when ports.port_id is not NULL and pos.position_speed < 2.0 then 'in_port' 
            -- Si le navire est détecté dans un port à une vitesse supérieure à 2 nœuds, on considère qu'il est en mer
            when ports.port_id is not NULL and pos.position_speed >= 2.0 then 'transiting_in_port_area' 
            -- Si aucune condition n'est remplie, on considère que la position est inconnue
            else 'unknown' 
        end as position_status -- Statut de la position du navire

    from drop_same_position as pos
    left join ports as ports
        on pos.position_point && ports.port_geometry_buffer
        and st_dwithin( -- Prétraitement sur BBox avec radius
                st_transform(pos.position_point, 3857), -- Passage en unités métriques
                st_transform(ports.port_geometry_point, 3857), -- Passage en unités métriques
                ports.port_buffer_size_m
            ) 
        and st_intersects(pos.position_point, ports.port_geometry_buffer) -- Intersection avec le buffer Voronoi des ports
),

-- Ne conserver que les positions pour lesquelles le bateau n'est pas stationné dans le même port que la position précédente

lag_position_status as ( -- Comparer la situation de la position courante avec la précédente du point de vue du port
    select 
        *,
        lag(is_in_port) OVER w as is_in_port_prev,
        lag(port_id) OVER w as port_id_prev,
        lag(position_status) OVER w as position_status_prev
    from positions_x_ports
    WINDOW w AS (PARTITION BY vessel_id ORDER BY position_timestamp)
),

position_of_interest as ( -- Conserver uniquement les positions qui ont un intérêt pour l'analyse
    select 
        *,
        coalesce(is_in_port and is_in_port_prev and port_id = port_id_prev, FALSE) as is_same_port
    from lag_position_status
    where 
        -- On conserve la première position connue
        is_first_position = TRUE
        -- On conserve la dernière position connue
        or is_last_position = TRUE
        -- On conserve les positions pour lesquelles le navire est en mouvement ou quand le statut est inconnu
        or position_status in ('unknown','at_sea','transiting_in_port_area') 
        -- On conserve les positions pour lesquelles le navire était précédemment en mouvement
        or position_status_prev in ('at_sea','transiting_in_port_area') 
        -- On conserve les positions pour lesquelles le navire n'est pas en mouvement, mais a changé de statut de position
        or position_status_prev != position_status 
        -- On conserve les positions pour lesquelles le navire est toujours stationné, mais dans un port différent de la position précédente
        or ((position_status = 'in_port' and position_status_prev = 'in_port') and not port_id = port_id_prev ) 
),

------------------------- Définition des débuts et fins d'excursions à partir des positions des navires -------------------------------------
excursions_define as ( -- Définition des excursions à partir des évolutions de la position du point de vue du port
    -- Une excursion débute lorsque le navire sort du périmètre portuaire dans lequel il était stationné ou 
    -- Une excursion se termine lorsqu'un navire situé dans un périmètre portuaire voit sa vitesse tomber sous 2 nœuds
	select 
		*,
		-- La position courante débute-t-elle une excursion ?
        case 
            -- La première position connue pour un navire est, s'il n'est pas au port, considérée comme le début d'une excursion
            when is_first_position and position_status != 'in_port' then TRUE 
            -- La première position connue pour un navire n'est pas, s'il est au port, considérée comme le début d'une excursion
            when is_first_position and position_status = 'in_port' then FALSE
            -- Le bateau était précédemment stationné dans un port et a changé de statut
            when position_status_prev = 'in_port' and position_status != 'in_port' then TRUE 
            -- Le bateau était déjà précédemment stationné dans un port mais a changé de port
            when position_status_prev = 'in_port' and position_status = 'in_port' and not is_same_port then TRUE 
            else FALSE
        end as is_excursion_start, 
        
        -- La position courante termine-t-elle une excursion ?
        case 
            -- Le bateau est stationné dans un port, ce n'était pas le cas précédemment
            when position_status = 'in_port' and position_status_prev != 'in_port' then TRUE 
            -- Le bateau était déjà précédemment stationné dans un port mais a changé de port  
            when position_status = 'in_port' and position_status_prev = 'in_port' and not is_same_port then TRUE 
            else FALSE
        end as is_excursion_end
	from position_of_interest
),

-------------------------------------------- Cacul de métriques basiques sur les positions ---------------------------------------------

diff_between_positions as ( -- Calcul des différences entre la position courante et la précédente
    select
        *,  
        -- Temps écoulé entre la position courante et la précédente (en secondes)
        extract(epoch from (position_timestamp - position_timestamp_prev)) as time_diff_s, 
        -- Distance euclidienne entre la position courante et la précédente (en mètres)
        (st_distance(st_transform(position_point_prev, 3857), st_transform(position_point, 3857))) as distance_m 
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
    position_id,
    position_id_prev,
    position_timestamp,
    position_timestamp_prev,
    cast(date_trunc('day', position_timestamp) AS date) AS position_timestamp_day,
    to_char(position_timestamp, 'YYYYMM') AS position_timestamp_month,

    position_mmsi,
    vessel_id,
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
    port_id_prev as port_exited, -- Le port dans lequel se trouvait la position précédente

    position_status, -- Statut de la position courante
    position_status_prev, -- Statut de la position précédente
    is_excursion_start, -- La position courante débute-t-elle une excursion ? 
    is_excursion_end, -- La position courante termine-t-elle une excursion ?

    time_diff_s, -- Temps écoulé entre la position courante et la précédente (en secondes)
    time_diff_h, -- Temps écoulé entre la position courante et la précédente (  en heures)
    distance_m, -- Distance euclidienne entre la position courante et la précédente (en mètres)
    distance_km, -- Distance euclidienne entre la position courante et la précédente (en kilomètres)
    distance_mi, -- Distance euclidienne entre la position courante et la précédente (en milles marins)

    position_point, -- Position géographique de la position courante
    position_point_prev, -- Position géographique de la position précédente
    nb_ais_messages, -- Nombre de messages AIS reçus pour cette position
    now() as position_itm_created_at -- Date de création de la position dans la base de données (cette table)

from vessel_positions_w_diff_convert

where TRUE 
    --and existing_positions.position_id is null -- On ne garde que les nouvelles positions
    and is_anterior_position = FALSE -- On ne garde pas la position antérieure ajoutée seulement pour les LAG dans le microbatch
    and is_same_position = FALSE -- Exclure les positions identiques à la précédente
order by position_timestamp, vessel_id
