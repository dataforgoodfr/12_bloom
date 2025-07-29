-- assert_port_w_excursions_have_positive_time_total_port_call.sql
/*
    Vérifie que les ports avec des excursions ont une durées d'escales totales > 0
*/

select * from {{ ref('itm_ports_calls') }}
where has_excursions = true
and total_port_call_duration < interval '0 seconds'
