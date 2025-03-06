"""Tests the features that dragonfly_comparison adds to dragonfly_core Room2D."""
import pytest

from ladybug_geometry.geometry2d import Point2D
from ladybug_geometry.geometry3d import Point3D, Face3D
from honeybee.boundarycondition import boundary_conditions as bcs
from dragonfly.room2d import Room2D
from dragonfly.windowparameter import SimpleWindowRatio
from dragonfly.shadingparameter import Overhang
from dragonfly.skylightparameter import GriddedSkylightRatio

from dragonfly_comparison.properties.room2d import Room2DComparisonProperties


def test_comparison_properties():
    """Test the existence of the Room2D comparison properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    overhang = Overhang(1)
    boundarycs = (bcs.outdoors, bcs.ground, bcs.outdoors, bcs.ground)
    window = (ashrae_base, None, ashrae_base, None)
    shading = (overhang, None, None, None)
    room = Room2D('SquareShoebox', Face3D(pts), 3, boundarycs, window, shading)

    assert hasattr(room.properties, 'comparison')
    assert isinstance(room.properties.comparison, Room2DComparisonProperties)


def test_comparison_properties_setability():
    """Test the auto-assigning of Room2D properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.is_top_exposed = True
    room.set_outdoor_window_parameters(ashrae_base)
    room.skylight_parameters = GriddedSkylightRatio(0.05)

    assert room.properties.comparison.comparison_floor_geometry is None
    assert room.properties.comparison.comparison_windows is None
    assert room.properties.comparison.comparison_skylight is None
    assert room.properties.comparison.floor_area_difference == 0
    assert room.properties.comparison.wall_sub_face_area_difference == 0
    assert room.properties.comparison.roof_sub_face_area_difference == 0

    room.properties.comparison.reset()
    assert isinstance(room.properties.comparison.comparison_floor_geometry, Face3D)
    assert isinstance(room.properties.comparison.comparison_windows, tuple)
    assert isinstance(room.properties.comparison.comparison_skylight, GriddedSkylightRatio)
    assert room.properties.comparison.floor_area_difference == 0
    assert room.properties.comparison.wall_sub_face_area_difference == 0
    assert room.properties.comparison.roof_sub_face_area_difference == 0

    snap_points = (Point2D(10.5, 0), Point2D(10.5, 10.5))
    room.snap_to_points(snap_points, 1.0)
    assert room.properties.comparison.floor_area_difference == \
        pytest.approx(7.625, abs=1e-3)
    assert room.properties.comparison.wall_sub_face_area_difference == \
        pytest.approx(1.8142776, abs=1e-3)
    assert room.properties.comparison.roof_sub_face_area_difference == \
        pytest.approx(0.38125, abs=1e-3)
    assert room.properties.comparison.sub_face_area_difference == \
        pytest.approx(2.1955276, abs=1e-3)

    assert room.properties.comparison.floor_area_percent_change == \
        pytest.approx(7.625, abs=1e-3)
    assert room.properties.comparison.wall_sub_face_area_percent_change == \
        pytest.approx(3.779745, abs=1e-3)
    assert room.properties.comparison.roof_sub_face_area_percent_change == \
        pytest.approx(7.625, abs=1e-3)
    assert room.properties.comparison.sub_face_area_percent_change == \
        pytest.approx(4.1425, abs=1e-3)


def test_duplicate():
    """Test what happens to comparison properties when duplicating a Room2D."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room_original = Room2D('SquareShoebox', Face3D(pts), 3)
    room_original.is_top_exposed = True
    room_original.set_outdoor_window_parameters(ashrae_base)
    room_original.skylight_parameters = GriddedSkylightRatio(0.05)
    room_original.properties.comparison.reset()
    room_dup_1 = room_original.duplicate()

    assert room_original.properties.comparison.host is room_original
    assert room_dup_1.properties.comparison.host is room_dup_1
    assert room_original.properties.comparison.host is not \
        room_dup_1.properties.comparison.host

    assert room_original.properties.comparison.floor_area_difference == \
        room_dup_1.properties.comparison.floor_area_difference
    snap_points = (Point2D(10.5, 0), Point2D(10.5, 10.5))
    room_dup_1.snap_to_points(snap_points, 1.0)
    assert room_original.properties.comparison.floor_area_difference != \
        room_dup_1.properties.comparison.floor_area_difference


def test_to_dict():
    """Test the Room2D to_dict method with comparison properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.is_top_exposed = True
    room.set_outdoor_window_parameters(ashrae_base)
    room.skylight_parameters = GriddedSkylightRatio(0.05)

    rd = room.to_dict()
    assert 'properties' in rd
    assert rd['properties']['type'] == 'Room2DProperties'
    assert 'comparison' in rd['properties']
    assert rd['properties']['comparison']['type'] == 'Room2DComparisonProperties'
    assert 'floor_boundary' not in rd['properties']['comparison'] or \
        rd['properties']['comparison']['floor_boundary'] is None
    assert 'window_parameters' not in rd['properties']['comparison'] or \
        rd['properties']['comparison']['window_parameters'] is None
    assert 'skylight_parameters' not in rd['properties']['comparison'] or \
        rd['properties']['comparison']['skylight_parameters'] is None

    room.properties.comparison.reset()
    snap_points = (Point2D(10.5, 0), Point2D(10.5, 10.5))
    room.snap_to_points(snap_points, 1.0)
    rd = room.to_dict()
    assert rd['properties']['comparison']['floor_boundary'] is not None
    assert len(rd['properties']['comparison']['window_parameters']) == 4
    assert rd['properties']['comparison']['skylight_parameters'] is not None


def test_from_dict():
    """Test the Room2D from_dict method with comparison properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.is_top_exposed = True
    room.set_outdoor_window_parameters(ashrae_base)
    room.skylight_parameters = GriddedSkylightRatio(0.05)
    room.properties.comparison.reset()
    snap_points = (Point2D(10.5, 0), Point2D(10.5, 10.5))
    room.snap_to_points(snap_points, 1.0)

    rd = room.to_dict()
    new_room = Room2D.from_dict(rd)
    assert new_room.properties.comparison.floor_area_difference == \
        pytest.approx(7.625, abs=1e-3)
    assert new_room.properties.comparison.wall_sub_face_area_difference == \
        pytest.approx(1.8142776, abs=1e-3)
    assert new_room.properties.comparison.roof_sub_face_area_difference == \
        pytest.approx(0.38125, abs=1e-3)
    assert new_room.properties.comparison.sub_face_area_difference == \
        pytest.approx(2.1955276, abs=1e-3)
    assert new_room.to_dict() == rd
