"""Tests the features that dragonfly_comparison adds to Model."""
import pytest

from ladybug_geometry.geometry2d import Point2D
from ladybug_geometry.geometry3d import Point3D, Face3D
from dragonfly.windowparameter import SimpleWindowRatio
from dragonfly.skylightparameter import GriddedSkylightRatio
from dragonfly.model import Model
from dragonfly.building import Building
from dragonfly.story import Story
from dragonfly.room2d import Room2D


def test_from_dict():
    """Test the Room from_dict method with doe2 properties."""
    pts = (Point3D(0, 0, 3), Point3D(10, 0, 3), Point3D(10, 10, 3), Point3D(0, 10, 3))
    ashrae_base = SimpleWindowRatio(0.4)
    room = Room2D('SquareShoebox', Face3D(pts), 3)
    room.is_top_exposed = True
    room.set_outdoor_window_parameters(ashrae_base)
    room.skylight_parameters = GriddedSkylightRatio(0.05)
    room.properties.comparison.reset()
    snap_points = (Point2D(10.5, 0), Point2D(10.5, 10.5))
    room.snap_to_points(snap_points, 1.0)

    story = Story('Office_Floor', [room])
    story.multiplier = 4
    building = Building('Office_Building', [story])
    model = Model('New_Development', [building])

    model_dict = model.to_dict()
    new_model = Model.from_dict(model_dict)
    assert new_model.to_dict() == model_dict

    new_room = new_model.room_2ds[0]
    assert new_room.properties.comparison.floor_area_difference == \
        pytest.approx(7.625, abs=1e-3)
    assert new_room.properties.comparison.wall_sub_face_area_difference == \
        pytest.approx(1.8142776, abs=1e-3)
    assert new_room.properties.comparison.roof_sub_face_area_difference == \
        pytest.approx(0.38125, abs=1e-3)
    assert new_room.properties.comparison.sub_face_area_difference == \
        pytest.approx(2.1955276, abs=1e-3)
