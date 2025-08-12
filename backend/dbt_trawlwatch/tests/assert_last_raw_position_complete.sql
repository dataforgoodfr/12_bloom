-- tests/assert_last_raw_position_complete.sql
/*
    This test checks that the number of vessels in the last RAW positions table matches the number of distinct vessel_id in the dimension table.
*/

with expected as (
    select count(distinct v.vessel_id) as expected_count
    from {{ ref('stg_dim_vessels') }} as v

),

actual as (
    select count(*) as actual_count
    from {{ ref('itm_vessel_last_raw_position') }}
)

select 
    actual.actual_count,
    expected.expected_count
from actual
inner join expected on true
where actual.actual_count != expected.expected_count
