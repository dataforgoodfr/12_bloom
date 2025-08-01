-- assert_first_and_last_position_complete.sql
/*
    This test checks that the number of vessels in the first and last positions table matches the number of distinct vessel_id in the dimension table.
*/

with expected as (
    select count(distinct vessel_id) as expected_count
    from {{ ref('stg_dim_vessels') }}
),

actual as (
    select count(*) as actual_count
    from {{ ref('itm_vessel_first_and_last_positions') }}
)

select 
    actual.actual_count,
    expected.expected_count
from actual
join expected on true
where actual.actual_count != expected.expected_count