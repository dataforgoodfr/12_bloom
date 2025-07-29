-- assert_port_w_excursions_have_at_least_one_port_call.sql
/*
    Vérifie que les ports avec des excursions ont au moins une escale.
*/

select * from {{ ref('itm_ports_calls') }}
where has_excursions = true
and port_calls_count < 1
