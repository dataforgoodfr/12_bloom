from shapely import Polygon

from bloom.domain.vessel import Vessel


def execute_rule_low_speed(vessel: Vessel, polygon_list: list[Polygon]) -> bool:
    threshold = 2
    if (
        len(polygon_list[polygon_list.contains(vessel.position)]) > 0
        and vessel.speed < threshold
    ):
        return True
    return False


def execute_rule_speed_in_five_and_seven(
    vessel: Vessel,
    polygon_list: list[Polygon],
) -> bool:
    min_threshold = 5.0
    max_threshold = 7.0
    if len(polygon_list[polygon_list.contains(vessel.position)]) > 0 and (
        min_threshold < vessel.speed < max_threshold
    ):
        return True
    return False


# TODO: rename Vessel class in VesselPosition
def execute_rule_trajectory_never_in_protected_area(
    vessel_positions_list: list[Vessel],
    polygon_list: list[Polygon],
) -> bool:
    for vessel_position in vessel_positions_list:
        if len(polygon_list[polygon_list.contains(vessel_position.position)]) > 0:
            return True
    return False
