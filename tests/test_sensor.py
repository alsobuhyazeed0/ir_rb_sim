import pytest
import math

from ir_rb_sim.config import DEFAULT_CONFIG
from ir_rb_sim.geometry import Pose, normalize_angle_deg, angular_diff_deg, relative_bearing_and_distance
from ir_rb_sim.sensor import build_sensor_ring, visible_units

def test_normalize_angle_deg_wraps_correctly():
    assert normalize_angle_deg(-30) == pytest.approx(330.0)
    assert normalize_angle_deg(370) == pytest.approx(10.0)
    assert normalize_angle_deg(360) == pytest.approx(0.0)
    assert normalize_angle_deg(0) == pytest.approx(0.0)

def test_angular_diff_handles_wraparound():
    assert abs(angular_diff_deg(350, 10)) == 20
    assert abs(angular_diff_deg(10, 350)) == 20

def test_relative_bearing_and_distance_basic():
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(0, 10, heading_deg=0) 
    bearing, distance = relative_bearing_and_distance(observer, target)
    assert distance == pytest.approx(10.0)
    assert bearing == pytest.approx(90.0)

def test_ring_has_correct_number_and_spacing():
    ring = build_sensor_ring()
    assert len(ring) == DEFAULT_CONFIG.NUM_SENSOR_UNITS
    headings = [u.heading_offset_deg for u in ring]
    assert headings == [i * DEFAULT_CONFIG.SENSOR_SPACING_DEG for i in range(8)]

def test_directly_ahead_hits_unit_0_only():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(10, 0, heading_deg=0)
    assert visible_units(observer, target, ring) == [0]

def test_directly_behind_hits_unit_4_only():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(-10, 0, heading_deg=0)
    assert visible_units(observer, target, ring) == [4]

def test_out_of_range_sees_nothing():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(DEFAULT_CONFIG.MAX_RANGE_CM + 10, 0, heading_deg=0)
    assert visible_units(observer, target, ring) == []

def test_at_exact_max_range_is_still_visible():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(DEFAULT_CONFIG.MAX_RANGE_CM, 0, heading_deg=0)
    assert visible_units(observer, target, ring) == [0]

def test_observer_heading_rotates_which_unit_sees_target():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=45)
    target = Pose(10 * math.cos(math.radians(45)), 10 * math.sin(math.radians(45)), heading_deg=0)
    assert visible_units(observer, target, ring) == [0]

def test_boundary_angle_is_shared_by_two_adjacent_units():
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    half = DEFAULT_CONFIG.SECTOR_HALF_ANGLE_DEG
    target = Pose(10 * math.cos(math.radians(half)), 10 * math.sin(math.radians(half)), heading_deg=0)
    seen = visible_units(observer, target, ring)
    assert set(seen) == {0, 1}

@pytest.mark.parametrize("bearing_deg", list(range(0, 360, 5)))
def test_every_bearing_has_at_least_one_covering_unit(bearing_deg):
    ring = build_sensor_ring()
    observer = Pose(0, 0, heading_deg=0)
    target = Pose(10 * math.cos(math.radians(bearing_deg)), 10 * math.sin(math.radians(bearing_deg)), heading_deg=0)
    assert len(visible_units(observer, target, ring)) >= 1