from time import perf_counter

from bloom.container import UseCases
from bloom.domain.rel_segment_zone import RelSegmentZone
from bloom.infra.repositories.repository_rel_segment_zone import RelSegmentZoneRepository
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.logger import logger


def run():
    use_cases = UseCases()
    db = use_cases.db()
    segment_repository = use_cases.segment_repository()
    excursion_repository = use_cases.excursion_repository()
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "rel_segments_zones"
        )
        logger.info(f"Lecture des segments créés/modifiés depuis le {point_in_time}")
        result = segment_repository.find_segments_in_zones_created_updated_after(session, point_in_time)
        logger.info(f"Traitement de {len(result)} segment(s)")
        new_rels = []
        excursions = {}
        segments = []
        max_created_updated = point_in_time
        for segment, zones in result.items():
            segment.in_costal_waters = False
            segment.in_amp_zone = False
            segment.in_territorial_waters = False
            for zone in zones:
                new_rels.append(RelSegmentZone(segment_id=segment.id, zone_id=zone.id))
                if zone.category == "amp":
                    segment.in_amp_zone = True
                elif zone.category == "coastal":
                    segment.in_costal_waters = True
                elif zone.category == "territorial":
                    segment.in_territorial_waters = True
            # Mise à jour de l'excursion avec le temps passé dans chaque type de zone
            excursion = excursions.get(segment.excursion_id,
                                       excursion_repository.get_excursion_by_id(session, segment.excursion_id))
            excursion.excursion_duration += segment.segment_duration
            if segment.in_amp_zone:
                excursion.total_time_in_amp += segment.segment_duration
            if segment.in_costal_waters:
                excursion.total_time_fishing_in_costal_waters += segment.segment_duration
            if segment.in_territorial_waters:
                excursion.total_time_in_territorial_waters += segment.segment_duration
            excursions[excursion.id] = excursion

            # Détection de la borne supérieure du traitement
            if segment.updated_at and segment.updated_at > max_created_updated:
                max_created_updated = segment.updated_at
            elif segment.created_at > max_created_updated:
                max_created_updated = segment.created_at
            segments.append(segment)
        excursion_repository.batch_update_excursion(session, excursions.values())
        logger.info(f"{len(excursions.values())} excursions mises à jour")
        segment_repository.batch_update_segment(session, segments)
        logger.info(f"{len(segments)} segments mis à jour")
        RelSegmentZoneRepository.batch_create_rel_segment_zone(session, new_rels)
        logger.info(f"{len(new_rels)} associations(s) créées")
        TaskExecutionRepository.set_point_in_time(session, "rel_segments_zones", max_created_updated)

        session.commit()


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Association des segments aux zones traversées")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Association des segments aux zones traversées en {duration:.2f}s")
