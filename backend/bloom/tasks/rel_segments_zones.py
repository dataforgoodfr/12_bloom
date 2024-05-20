from time import perf_counter
from bloom.logger import logger
from bloom.container import UseCases
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.domain.rel_segment_zone import RelSegmentZone


def run():
    use_cases = UseCases()
    db = use_cases.db()
    segment_repository = use_cases.segment_repository()
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "rel_segments_zones"
        )
        result = segment_repository.find_segments_in_zones_created_updated_after(session, point_in_time)
        logger.info(f"Traitement de {len(result)} segment(s)")
        new_rels = []
        for segment, zones in result.items():
            for zone in zones:
                new_rels.append(RelSegmentZone(segment_id=segment.id, zone_id=zone.id))
                if zone.category == "amp":
                    segment.in_amp_zone = True
                elif zone.category == "coastal":
                    segment.in_costal_waters = True
                elif zone.category == "territorial":
                    segment.in_territorial_waters = True


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Association des segments aux zones traversées")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Association des segments aux zones traversées en {duration:.2f}s")
