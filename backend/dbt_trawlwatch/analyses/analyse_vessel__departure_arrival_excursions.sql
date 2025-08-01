SELECT * FROM (
    SELECT excursion_id, departure_at::date, excursion_start_position_timestamp_day, arrival_at::date, excursion_end_position_timestamp_day FROM fct_excursion fe 
    LEFT JOIN (SELECT * FROM itm.itm_vessel_excursions ve WHERE ve.vessel_id = 'NLD199802182') AS foo
    ON departure_at::date = foo.excursion_start_position_timestamp_day OR arrival_at::date = foo.excursion_end_position_timestamp_day
    WHERE fe.vessel_id = 11 AND departure_at < '2025-02-08' AND departure_at::date NOT IN ('2024-04-11', '2024-05-13', '2024-08-29')
    ) AS foo2
WHERE excursion_start_position_timestamp_day IS NULL