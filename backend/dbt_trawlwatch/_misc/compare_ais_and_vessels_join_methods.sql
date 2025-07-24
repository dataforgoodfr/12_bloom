-- Comparer la qualité de jointure entre données AIS et dim_vessel en fonction des champs utilisés
with

ais_data as (
	select 
	id as ais_id, created_at, position_timestamp, --position_longitude, position_latitude, --infos AIS essentielles
	vessel_mmsi, vessel_imo, vessel_callsign, vessel_flag, vessel_name,-- Infos d'identification du navir
	vessel_width, vessel_length, vessel_ship_type, vessel_sub_ship_type
	from public.spire_ais_data
	order by created_at desc
	limit 10000
),

nb_ais_data as ( select count(*) as nb_true_rows from ais_data ),

vessels_mmsi as (
	select id as v_id, mmsi as v_mmsi, imo as v_imo, country_iso3 as v_country_iso3, ship_name, ircs, width, length, 'mmsi'::varchar as joined_on
	from dim_vessel
	where tracking_activated is true
),

vessels_imo as (
	select id as v_id, mmsi as v_mmsi, imo as v_imo, country_iso3 as v_country_iso3, ship_name, ircs, width, length, 'imo'::varchar as joined_on
	from dim_vessel
	where tracking_activated is true
),


vessels_callsign as (
	select id as v_id, mmsi as v_mmsi, imo as v_imo, country_iso3 as v_country_iso3, ship_name, ircs, width, length, 'callsign'::varchar as joined_on
	from dim_vessel
	where tracking_activated is true
),

vessels_misc as (
	select id as v_id, mmsi as v_mmsi, imo as v_imo, country_iso3 as v_country_iso3, ship_name, ircs, width, length, '_misc_'::varchar as joined_on
	from dim_vessel
	where tracking_activated is true
),

join_it as (
	select a.*, n.nb_true_rows, v1.joined_on as v1_joined_on, v2.joined_on as v2_joined_on, v3.joined_on as v3_joined_on, v4.joined_on as v4_joined_on
	from ais_data a
	left join nb_ais_data n on true
	left join vessels_mmsi v1 on (a.vessel_mmsi) = (v1.v_mmsi) 
	left join vessels_imo v2 on (a.vessel_imo) = (v2.v_imo)
	left join vessels_callsign v3 on (a.vessel_callsign) = (v3.ircs)
	left join vessels_misc v4 on (a.vessel_mmsi) = (v4.v_mmsi) 
			and (
					(a.vessel_imo) = (v4.v_imo) or
					(a.vessel_callsign = v4.ircs) or
					(vessel_width, vessel_length) = (v4.width, v4.length) or
					(vessel_name, vessel_flag) = (v4.ship_name, v4.v_country_iso3)
				)
)

SELECT
    max(nb_true_rows)                                 AS nb_total,
    COUNT(*) FILTER (WHERE v1_joined_on = 'mmsi')      AS nb_match_mmsi,
    COUNT(*) FILTER (WHERE v2_joined_on = 'imo')       AS nb_match_imo,
    COUNT(*) FILTER (WHERE v3_joined_on = 'callsign')  AS nb_match_callsign,
	COUNT(*) FILTER (WHERE v4_joined_on = '_misc_')  AS nb_match_misc
FROM join_it

--select * from join_it
