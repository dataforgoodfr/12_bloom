# Useful SQL examples

List of mmi scrapped since last update :\
`SELECT mmsi as tm FROM spire_vessel_positions WHERE timestamp > '2023-06-17' GROUP BY mmsi`

More recent timestamp scrapped since last update :\
`SELECT tm,array_agg(mmsi) FROM (SELECT mmsi,max(timestamp) as tm FROM spire_vessel_positions WHERE timestamp > '2023-06-17' GROUP BY mmsi) as foo GROUP BY tm`

mmsi not scrapped by Spire :\
`SELECT mmsi FROM vessels WHERE mmsi IS NOT NULL AND mmsi NOT IN (SELECT mmsi as tm FROM spire_vessel_positions WHERE timestamp > '2023-06-17' GROUP BY mmsi)`

number of distincte position per boat which has more than 1000 positions gathered :\
`SELECT * FROM (SELECT COUNT(*) as sum_position,mmsi FROM (SELECT DISTINCT position,mmsi FROM spire_vessel_positions) as foo GROUP BY mmsi) as bar WHERE sum_position > 1000`