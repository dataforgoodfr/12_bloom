from shapely import Point, Polygon

from bloom.infra.repositories.file_repository_polygons import PolygonFileRepository


def test_is_point_in_polygon_returns_false_when_point_is_not_in_polygons_list():
    polygon_repository = PolygonFileRepository()
    polygon_repository.load_polygons()
    point = Point(49.69989, -6.512513)

    assert not polygon_repository.is_point_in_polygons(point)


def test_is_point_in_polygon_returns_polygon_when_point_is_in_polygons_list():
    polygon_repository = PolygonFileRepository()
    polygon_repository.load_polygons()
    point = Point(-61.85589548359167, 17.195012165330123)
    polygon_coordinates = [
        Point(-61.82493782199998, 17.184972703000028),
        Point(-61.82497470499993, 17.184977660000072),
        Point(-61.88691617799998, 17.185021894000045),
        Point(-61.88677082899994, 17.204998586000045),
        Point(-61.825089039999966, 17.20508254400005),
        Point(-61.82493782199998, 17.184972703000028),
    ]
    expected_polygon = Polygon(polygon_coordinates)

    actual_polygon = polygon_repository.is_point_in_polygons(point)

    assert expected_polygon == actual_polygon
