"""Tests for ir_rb_sim.robot (Robot: Pose + sensor ring container)."""

from ir_rb_sim.geometry import Pose
from ir_rb_sim.robot import Robot
from ir_rb_sim.sensor import visible_units
from ir_rb_sim.config import DEFAULT_CONFIG


def test_robot_create_builds_full_sensor_ring():
    r = Robot.create(id=0, pose=Pose(0, 0, 0))
    assert len(r.sensor_ring) == DEFAULT_CONFIG.NUM_SENSOR_UNITS


def test_visible_units_to_matches_raw_function():
    """Robot.visible_units_to must give the exact same answer as calling
    the underlying visible_units() function directly - it's just a
    convenience wrapper, not different logic."""
    r0 = Robot.create(id=0, pose=Pose(0, 0, heading_deg=0))
    r1 = Robot.create(id=1, pose=Pose(10, 0, heading_deg=0))

    expected = visible_units(r0.pose, r1.pose, r0.sensor_ring)
    assert r0.visible_units_to(r1) == expected
    assert r0.visible_units_to(r1) == [0]


def test_visibility_is_directional():
    """r0 sees r1 straight ahead (unit 0), but r1 - facing the same way -
    sees r0 as directly BEHIND it (unit 4), not the same unit."""
    r0 = Robot.create(id=0, pose=Pose(0, 0, heading_deg=0))
    r1 = Robot.create(id=1, pose=Pose(10, 0, heading_deg=0))

    assert r0.visible_units_to(r1) == [0]
    assert r1.visible_units_to(r0) == [4]