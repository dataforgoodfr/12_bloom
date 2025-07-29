-- assert_no_more_than_1_open_ongoing_excursion_per_vessel
-- This test checks that there is no more than one open/ongoing excursion per vessel.

select vessel_id from {{ ref('itm_vessel_excursions') }}
where excursion_status = 'ongoing'
group by vessel_id
having count(*) > 1
