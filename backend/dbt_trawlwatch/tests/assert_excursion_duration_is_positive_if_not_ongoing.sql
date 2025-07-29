-- assert_excursion_duration_is_positive_if_not_ongoing.sql
-- This test checks that the excursion duration is positive if the excursion is not ongoing.
select excursion_id
from {{ ref('itm_vessel_excursions') }}
where excursion_status != 'ongoing'
    and excursion_duration_interval <= interval '0 seconds'
