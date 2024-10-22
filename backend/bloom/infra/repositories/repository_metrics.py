       stmt = select(
            sql_model.Vessel.id,
            #sql_model.Segment.excursion_id,
            sql_model.Vessel.mmsi
            sql_model.Segment.in_amp_zone #segment dans une zone ou non
            sql_model.Segment.type #default d'ais ou pas

        ).join(
            sql_model.Excursion,
            sql_model.Segment.excursion_id == sql_model.Excursion.id

        ).join(
            sql_model.Vessel,
            sql_model.Excursion.vessel_id == sql_model.Vessel.id

        ).filter(
            sql_model.Segment.last_vessel_segment == True
        )