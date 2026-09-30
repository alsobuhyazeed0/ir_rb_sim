import random

import numpy as np
import pytest

from ir_rb_sim.config import DEFAULT_CONFIG
from ir_rb_sim.geometry import Pose
from ir_rb_sim.ranging import DistanceLevel
from ir_rb_sim.world import World, WorldRobot


def _make_world(robots, seed=0):
    return World(
        robots=robots,
        rng=np.random.default_rng(seed),
        py_rng=random.Random(seed),
    )


def test_lone_robot_detects_nothing():
    r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    world = _make_world([r0])
    result = world.step()[0]

    assert all(level == DistanceLevel.INF for level in result.levels)
    assert all(d is False for d in result.detected)


@pytest.mark.parametrize("seed", list(range(20)))
def test_two_robots_facing_each_other_both_detect(seed):
    r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    r1 = WorldRobot.create(id=1, pose=Pose(10, 0, heading_deg=180), seed=2)
    world = _make_world([r0, r1], seed=seed)
    results = world.step()

    for rid in (0, 1):
        res = results[rid]
        assert res.detected[0] is True
        assert res.levels[0] != DistanceLevel.INF
        # every other unit sees nothing - the other robot is only in unit
        # 0's sector for both robots in this head-on arrangement
        for u in range(1, DEFAULT_CONFIG.NUM_SENSOR_UNITS):
            assert res.detected[u] is False
            assert res.levels[u] == DistanceLevel.INF


def test_robot_out_of_range_is_not_detected():
    far = DEFAULT_CONFIG.MAX_RANGE_CM + 5.0
    r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    r1 = WorldRobot.create(id=1, pose=Pose(far, 0, heading_deg=180), seed=2)
    world = _make_world([r0, r1])
    results = world.step()

    for rid in (0, 1):
        res = results[rid]
        assert all(level == DistanceLevel.INF for level in res.levels)
        assert all(d is False for d in res.detected)


@pytest.mark.parametrize("r1_heading_deg", [0.0, 20.0, 90.0, 137.0, 271.0])
def test_full_ring_coverage_gives_mutual_visibility_at_any_heading(r1_heading_deg):
    r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    r1 = WorldRobot.create(id=1, pose=Pose(10, 0, heading_deg=r1_heading_deg), seed=2)
    world = _make_world([r0, r1])
    results = world.step()

    for rid in (0, 1):
        res = results[rid]
        assert any(level != DistanceLevel.INF for level in res.levels)
        assert any(d is True for d in res.detected)


def test_out_of_range_breaks_reciprocity_even_though_ring_covers_all_angles():
    far = DEFAULT_CONFIG.MAX_RANGE_CM + 5.0
    r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    r1 = WorldRobot.create(id=1, pose=Pose(far, 0, heading_deg=33.0), seed=2)
    world = _make_world([r0, r1])
    results = world.step()

    for rid in (0, 1):
        res = results[rid]
        assert all(level == DistanceLevel.INF for level in res.levels)
        assert all(d is False for d in res.detected)


@pytest.mark.parametrize("seed", list(range(10)))
def test_three_robots_in_a_line_middle_one_sees_both_sides(seed):
    a = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
    m = WorldRobot.create(id=1, pose=Pose(10, 0, heading_deg=180), seed=2)
    b = WorldRobot.create(id=2, pose=Pose(20, 0, heading_deg=180), seed=3)

    world = _make_world([a, m, b], seed=seed)
    results = world.step()

    res_m = results[1]
    assert res_m.detected[0] is True  # facing A (heading offset 0 -> -x)
    assert res_m.detected[4] is True  # facing B (heading offset 180 -> +x)
    assert res_m.levels[0] != DistanceLevel.INF
    assert res_m.levels[4] != DistanceLevel.INF

    res_a = results[0]
    assert res_a.detected[0] is True
    res_b = results[2]
    assert res_b.detected[0] is True


def test_step_is_reproducible_with_same_seeds():
    def build():
        r0 = WorldRobot.create(id=0, pose=Pose(0, 0, heading_deg=0), seed=1)
        r1 = WorldRobot.create(id=1, pose=Pose(10, 0, heading_deg=180), seed=2)
        return World(
            robots=[r0, r1],
            rng=np.random.default_rng(99),
            py_rng=random.Random(99),
        )

    result_a = build().step()
    result_b = build().step()

    for rid in (0, 1):
        assert result_a[rid].levels == result_b[rid].levels
        assert result_a[rid].detected == result_b[rid].detected