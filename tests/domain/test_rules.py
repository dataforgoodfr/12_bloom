from shapely import Point

from bloom.domain.vessel import Vessel
from bloom.infra.file_repository_polygons import PolygonFileRepository
from bloom.domain.rules import (
    execute_rule_low_speed,
    execute_rule_speed_in_five_and_seven,
    execute_rule_trajectory_never_in_protected_area,
)

test_vessel = Vessel(
    timestamp="2023-03-12 12:31 UTC",
    ship_name="ZEELAND",
    IMO="8901913",
    last_position_time="2023-03-12 12:30 UTC",
    position=Point(-61.85589548359167, 17.195012165330123),
    status="ACTIVE",
    speed=0.0,
    navigation_status="Moored",
)


test_vessel_rule_2 = Vessel(
    timestamp="2023-03-12 12:31 UTC",
    ship_name="ZEELAND",
    IMO="8901913",
    last_position_time="2023-03-12 12:30 UTC",
    position=Point(-61.85589548359167, 17.195012165330123),
    status="ACTIVE",
    speed=5.5,
    navigation_status="Moored",
)

faulty_vessel_positions_list = [
    Vessel(
        timestamp="2023-03-12 12:31 UTC",
        ship_name="Faulty position vessel",
        IMO="8901913",
        last_position_time="2023-03-12 12:30 UTC",
        position=Point(-61.85589548359167, 17.195012165330123),
        status="ACTIVE",
        speed=0.0,
        navigation_status="Moored",
    ),
    Vessel(
        timestamp="2023-03-12 12:31 UTC",
        ship_name="Faulty position vessel",
        IMO="8901913",
        last_position_time="2023-03-12 12:30 UTC",
        position=Point(-60.85589548359167, 10.195012165330123),
        status="ACTIVE",
        speed=0.0,
        navigation_status="Moored",
    ),
]

not_faulty_vessel_positions_list = [
    Vessel(
        timestamp="2023-03-12 12:31 UTC",
        ship_name="Not faulty position vessel",
        IMO="8901913",
        last_position_time="2023-03-12 12:30 UTC",
        position=Point(-10.85589548359167, 20.195012165330123),
        status="ACTIVE",
        speed=0.0,
        navigation_status="Moored",
    ),
    Vessel(
        timestamp="2023-03-12 12:31 UTC",
        ship_name="Not faulty position vessel",
        IMO="8901913",
        last_position_time="2023-03-12 12:30 UTC",
        position=Point(-60.85589548359167, 10.195012165330123),
        status="ACTIVE",
        speed=0.0,
        navigation_status="Moored",
    ),
]


def test_rule_low_speed_returns_true_for_vessel_too_quick_in_protected_polygon():
    # Given
    polygon_repository = PolygonFileRepository()
    polygon_repository.load_polygons()

    is_vessel_faulty = execute_rule_low_speed(
        vessel=test_vessel, polygon_list=polygon_repository.polygons
    )

    # Then
    assert is_vessel_faulty


def test_rule_speed_in_five_and_seven_returns_true_for_vessel_2_in_protected_polygon():
    # Given
    polygon_repository = PolygonFileRepository()
    polygon_repository.load_polygons()

    # When
    is_vessel_faulty = execute_rule_speed_in_five_and_seven(
        vessel=test_vessel_rule_2, polygon_list=polygon_repository.polygons
    )

    # Then
    assert is_vessel_faulty


def test_rule_trajectory_never_in_protected_area_returns_faulty_position():
    # Given
    polygon_repository = PolygonFileRepository()
    polygon_repository.load_polygons()

    is_first_vessel_faulty = execute_rule_trajectory_never_in_protected_area(
        faulty_vessel_positions_list, polygon_repository.polygons
    )
    is_second_vessel_faulty = execute_rule_trajectory_never_in_protected_area(
        not_faulty_vessel_positions_list, polygon_repository.polygons
    )

    assert is_first_vessel_faulty
    assert not is_second_vessel_faulty
