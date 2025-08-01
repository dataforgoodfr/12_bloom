SELECT * FROM (
SELECT ive.excursion_id, 
		EXTRACT(day from ive.excursion_duration_interval) * 86400 
			+ EXTRACT(hour from ive.excursion_duration_interval) * 60 * 60
			+ EXTRACT(minute from ive.excursion_duration_interval) * 60
			+ EXTRACT(SECOND FROM ive.excursion_duration_interval)
		AS excursion_duration_seconds, 
		sum(EXTRACT(hour from ivs.segment_duration) * 60 * 60 
			+ EXTRACT(minute from ivs.segment_duration) * 60
			+ EXTRACT(second from ivs.segment_duration)) 
		AS total_segments_duration
from itm.itm_vessel_excursions_details ive
LEFT JOIN itm.itm_vessel_segments ivs 
ON ive.excursion_id = ivs.excursion_id
GROUP BY ive.excursion_id, ive.excursion_duration_interval 
) AS foo
WHERE foo.excursion_duration_seconds != foo.total_segments_duration 