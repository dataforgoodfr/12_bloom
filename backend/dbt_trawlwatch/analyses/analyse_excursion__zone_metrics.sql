-- Selection d'une excursion sur l'interface de Trawl Watch
SELECT * FROM dim_vessel WHERE imo = 9175834;
SELECT * FROM fct_excursion fe WHERE vessel_id = 11 AND departure_at > '2025-02-07';
SELECT * FROM staging.stg_dim_vessels sdv WHERE dim_vessel_imo = '9175834';
SELECT * FROM itm.itm_vessel_excursions WHERE vessel_id = 'NLD199802182' AND excursion_start_position_timestamp > '2025-02-07';

-- Analyse des métriques de l'excursion entre V1 et V2 (hors durée de l'excursion)
SELECT * FROM (
SELECT 
	(extract(DAY FROM foo2.total_time_in_amp) * 60 * 60 * 24 
												+ extract(HOUR FROM foo2.total_time_in_amp) * 60 * 60 
												+ extract(MINUTE FROM foo2.total_time_in_amp) * 60 
												+ extract(second FROM foo2.total_time_in_amp)) AS ref_total_time_in_amp,
	sum(CASE WHEN is_in_amp_zone THEN segment_duration ELSE NULL end) AS total_time_in_amp,
	(extract(DAY FROM foo2.total_time_in_territorial_waters) * 60 * 60 * 24 
												+ extract(HOUR FROM foo2.total_time_in_territorial_waters) * 60 * 60 
												+ extract(MINUTE FROM foo2.total_time_in_territorial_waters) * 60 
												+ extract(second FROM foo2.total_time_in_territorial_waters)) AS ref_total_time_in_territorial_waters,
	sum(CASE WHEN is_in_territorial_waters THEN segment_duration_s ELSE NULL end) AS total_time_in_territorial_waters,
	(extract(DAY FROM foo2.total_time_in_zones_with_no_fishing_rights) * 60 * 60 * 24 
												+ extract(HOUR FROM foo2.total_time_in_zones_with_no_fishing_rights) * 60 * 60 
												+ extract(MINUTE FROM foo2.total_time_in_zones_with_no_fishing_rights) * 60 
												+ extract(second FROM foo2.total_time_in_zones_with_no_fishing_rights)) AS ref_total_time_in_zone_with_no_fishing_rights,	
	sum(CASE WHEN is_in_zone_with_no_fishing_rights THEN segment_duration_s ELSE NULL end) AS total_time_in_zone_with_no_fishing_rights,
	(extract(DAY FROM foo2.total_time_default_AIS) * 60 * 60 * 24 
											+ extract(HOUR FROM foo2.total_time_default_ais) * 60 * 60 
											+ extract(MINUTE FROM foo2.total_time_default_ais) * 60 
											+ extract(second FROM foo2.total_time_default_ais)) AS ref_total_time_default_AIS,
	sum(CASE WHEN segment_type = 'DEFAULT_AIS' THEN segment_duration_s ELSE NULL end) AS total_time_default_AIS
FROM itm.itm_vessel_segments 
JOIN (SELECT * FROM fct_excursion fe WHERE fe.id = 182922) AS foo2
ON true
WHERE excursion_id = 'NLD199802182_0021'
GROUP BY foo2.total_time_in_amp, foo2.total_time_in_territorial_waters, foo2.total_time_in_zones_with_no_fishing_rights, foo2.total_time_default_ais
) AS foo3
WHERE ref_total_time_in_territorial_waters != total_time_in_territorial_waters 
	OR foo3.ref_total_time_in_zone_with_no_fishing_rights != foo3.total_time_in_zone_with_no_fishing_rights
	-- or foo3.ref_total_time_in_amp != foo3.total_time_in_amp 