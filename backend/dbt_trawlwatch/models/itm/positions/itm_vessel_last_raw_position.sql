-- itm_vessel_last_raw_position.sql
/*
	Extraire la dernière position connue brute (RAW) par vessel_id
	
	Logique : Filtrer spire_ais_data au départ (sans tenir compte de dim_vessels) et ainsi limiter les larges jointures
	1. Scanner le moins possible des extraits larges de spire_ais_data, et sur un minimum de champs bien indexés : `id`, `vessel_mmsi`, `created_at`, `position_timestamp`
	2. Garder l’approche consistant à trouver un gain facile en exploitant les positions présentes dans la dernière remontée grâce à `created_at`
	3. Compléter par l’exploitation des `id` max (donc position située dans la dernière remontée dispo pour le navire)
	4. Joindre la dimension MMSI pour récupérer le `vessel_id` seulement à la fin (peu de lignes à joindre)

	Performance attendue : INIT < 2'30 contre 5-6' sur la version précédente, incrémental à tester
	>>> 1 618 lignes en sortie correspondant aux distinct vessel_id
*/

{{ config(
    schema = 'itm',
    materialized = 'incremental',
    incremental_strategy = 'merge',
    unique_key = ['vessel_id'],
    indexes = [
        {'columns': ['vessel_id'], 'type': 'btree'},
        {'columns': ['position_timestamp__raw_last'], 'type': 'btree'},
        {'columns': ['position_ais_created_at__raw_max'], 'type': 'btree'}
    ],
    pre_hook = [
        "SET work_mem = \'64MB\';"
    ]
) }}


with 

last_id as ( -- Obtenir l'id de la dernière remontée AIS par MMSI
	select  
		vessel_mmsi, 
		max(id) as lastid 
	from {{ source('spire', 'spire_ais_data') }}

    {% if is_incremental() %}
    WHERE created_at > (
      SELECT MAX(position_ais_created_at__raw_max)
      FROM {{ this }}
    )
    {% endif %}

	group by vessel_mmsi 
	order by vessel_mmsi
),

last_retrieval as ( -- Récupération de la dernière date de mise à jour des positions AIS
    select spire_retrieval_ts as last_retrieval
    from {{ ref('observ_spire_ais_data_retrievals') }}
    order by last_retrieval desc
    limit 1
),

data_from_last_retrieval as ( -- Extraire les données de la dernière remontée AIS
	select 
		'last_retrieval' as raw_origin,
		ais.vessel_mmsi, 
		ais.position_timestamp,
		ais.position_speed,
		ais.position_heading,
		ais.position_latitude,
		ais.position_longitude,
		ais.created_at
	from {{ source('spire', 'spire_ais_data') }} as ais
	inner join last_retrieval as lr 
		on  ais.created_at = lr.last_retrieval
	order by ais.vessel_mmsi
),

list_id_to_get as ( -- Identifier les id à remonter par jointure externe
	select lid.lastid--, lr.position_timestamp 
	from last_id as lid
	left join data_from_last_retrieval as lr on lid.vessel_mmsi = lr.vessel_mmsi
	where lr.position_timestamp is null
	order by lid.lastid
),

get_lastid_infos as ( -- Récupérer les infos des MMSI plus ancien que last_retrieval
	select 
		'oldies' as raw_origin,
		ais.vessel_mmsi, 
		ais.position_timestamp,
		ais.position_speed,
		ais.position_heading,
		ais.position_latitude,
		ais.position_longitude,
		ais.created_at
	from {{ source('spire', 'spire_ais_data') }} as ais
	inner join list_id_to_get as lid on ais.id = lid.lastid

    {% if is_incremental() %}
        WHERE ais.created_at > (
        SELECT MAX(position_ais_created_at__raw_max)
        FROM {{ this }}
        )
    {% endif %}
),

union_it as ( -- Toutes les last_raw_data disponibles
	select * from data_from_last_retrieval
	union 
	select * from get_lastid_infos
	order by position_timestamp
),

dim_mmsi as ( -- Dimension MMSI
	select 
		vessel_id, 
		dim_mmsi_mmsi,
		dim_mmsi_start_date,
		dim_mmsi_end_date
	from {{ ref('stg_dim_mmsi') }}
	order by dim_mmsi_mmsi, dim_mmsi_start_date, dim_mmsi_end_date
),

join_it as ( -- Jointure entre les dernières positions MMSI connues et la dimension MMSI pour récupérer les vessel_id (pour la période de validité MMSI)
	select 
		dim_mmsi.vessel_id,
		dim_mmsi.dim_mmsi_mmsi as position_mmsi__raw_last,
		last_raw.position_timestamp as position_timestamp__raw_last,
		last_raw.position_latitude as position_latitude__raw_last,
		last_raw.position_longitude as position_longitude__raw_last,
		last_raw.position_speed as position_speed__raw_last,
	 	last_raw.position_heading as position_heading__raw_last,
		last_raw.created_at as position_ais_created_at__raw_max,
		to_char(last_raw.position_timestamp, 'YYYYMM') as position_timestamp__raw_max_month,
		date_trunc('day', last_raw.position_timestamp) as position_timestamp__raw_max_day,
		st_setsrid(
			st_makepoint(
				last_raw.position_longitude,
				last_raw.position_latitude
			), 4326) as position_point__raw_last,
		now() as last_raw_position_evaluated_at,
    	last_raw.raw_origin as last_raw_position_origin
	from dim_mmsi
	{% if is_incremental() %}
    inner join union_it as last_raw
    {% else %}
    left join union_it as last_raw 
    {% endif %}
		on dim_mmsi.dim_mmsi_mmsi = last_raw.vessel_mmsi 
		and utils.safe_between(last_raw.position_timestamp, dim_mmsi.dim_mmsi_start_date, dim_mmsi.dim_mmsi_end_date)
),

get_last_val_by_vessel_id as ( -- Ne conserver que la dernière position par vessel_id
	select * from (
		select
			*,
			row_number() over (partition by vessel_id order by position_timestamp__raw_last desc) as rn
		from join_it
	) as ranked
	where rn = 1
)

select * from get_last_val_by_vessel_id
{% if is_incremental() %}
    WHERE position_timestamp__raw_last is not null
{% endif %}
