from bloom.container import UseCases
from bloom.logger import logger
from sqlalchemy.orm import Session
from bloom.domain.rel_segment_zone import RelSegmentZone
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from bloom.infra.repositories.repository_rel_segment_zone import RelSegmentZoneRepository







def run():

    use_cases = UseCases()
    db = use_cases.db()
    with db.session() as session:
        
        
        port_repository = use_cases.port_repository()
        segment_repository = use_cases.segment_repository()
        excursion_repository = use_cases.excursion_repository()

        result= segment_repository.find_segments_in_zones(session)
        new_rels = []
        excursions = {}
        segments = []
        for segment, zones in result.items():
            segment_in_zone = False
            for zone in zones:
                if segment.type == "DEFAULT_AIS":
                    continue
                segment_in_zone = True
                new_rels.append(RelSegmentZone(segment_id=segment.id, zone_id=zone.id))
                if zone.category == "amp":
                    segment.in_amp_zone = 1
                elif zone.category == "Fishing coastal waters (6-12 NM)" :
                    country_iso3 = segment_repository.get_vessel_attribute_by_segment(session, segment.id)
                    res = country_iso3 in zone.beneficiaries
                    if res is False :
                        segment.in_zone_with_no_fishing_rights = 1
                elif zone.category == "Territorial seas":
                    segment.in_territorial_waters = 1
            if segment_in_zone:
                segments.append(segment)
            # Mise à jour de l'excursion avec le temps passé dans chaque type de zone
            excursion = excursions.get(segment.excursion_id,
                                       excursion_repository.get_excursion_by_id(session, segment.excursion_id))
            if segment.in_amp_zone == 1:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_amp += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_amp += segment.segment_duration
            if segment.in_zone_with_no_fishing_rights == 1:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_zones_with_no_fishing_rights += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_zones_with_no_fishing_rights += segment.segment_duration
            if segment.in_territorial_waters == 1:
                if segment.type == "AT_SEA":
                    excursion.total_time_in_territorial_waters += segment.segment_duration
                elif segment.type == "FISHING":
                    excursion.total_time_fishing_in_territorial_waters += segment.segment_duration

            excursion.excursion_duration += segment.segment_duration
            if segment.type == "FISHING":
                excursion.total_time_fishing += segment.segment_duration
            elif segment.type == "DEFAULT_AIS":
                if excursion.total_time_default_ais is None:
                    excursion.total_time_default_ais = timedelta(0)
                excursion.total_time_default_ais += segment.segment_duration

            excursion.total_time_at_sea = excursion.excursion_duration - (
                    excursion.total_time_in_zones_with_no_fishing_rights + excursion.total_time_in_territorial_waters)

            excursions[excursion.id] = excursion

        
        excursion_repository.batch_update_excursion(session, excursions.values())
        logger.info(f"{len(excursions.values())} excursions mises à jour")
        segment_repository.batch_update_segment(session, segments)
        logger.info(f"{len(segments)} segments mis à jour")
        RelSegmentZoneRepository.batch_create_rel_segment_zone(session, new_rels)
        logger.info(f"{len(new_rels)} associations(s) créées")
       # vessels_ids = set(exc.vessel_id for exc in excursions.values())
       # if not vessels_ids:
        #    print("Aucun vessel_id fourni.")
        #    nb_last = segment_repository.update_last_segments(session, [])
       # else:
        #    nb_last = segment_repository.update_last_segments(session, vessels_ids)
        #    logger.info(f"{nb_last} derniers segments mis à jour")
        



        all_ports = port_repository.get_all_ports(session)
        port_repository.batch_update_ports_has_excursion(session, all_ports)
        logger.info(f"{len(all_ports)} ports mises à jour")

        session.commit()




