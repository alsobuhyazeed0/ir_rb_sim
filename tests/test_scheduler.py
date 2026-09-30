import random

import pytest

from ir_rb_sim.config import DEFAULT_CONFIG
from ir_rb_sim.ranging import DistanceLevel, LEVEL_TEST_DAC, make_ideal_detect_fn
from ir_rb_sim.scheduler import run_sensing_cycle


def _fixed_unit_detect_fns(overrides: dict) -> list:
    n = DEFAULT_CONFIG.NUM_SENSOR_UNITS
    fns = []
    for u in range(n):
        if u in overrides:
            i_min = LEVEL_TEST_DAC[overrides[u]]
        else:
            i_min = DEFAULT_CONFIG.DAC_MAX + 1
        fns.append(make_ideal_detect_fn(i_min))
    return fns


def test_paper_worked_example_fig19():
    detect_fns = _fixed_unit_detect_fns({1: 4, 5: 5})

    def signal_present_fn(u, round_index):
        if u == 1 and round_index == 0:
            return True
        if u == 5 and round_index == DEFAULT_CONFIG.ROUNDS_PER_PHASE1:
            return True
        return False

    rng = random.Random(42)
    result = run_sensing_cycle(detect_fns, signal_present_fn, rng=rng)

    assert result.levels[1] == DistanceLevel.L4
    assert result.levels[5] == DistanceLevel.L5
    assert result.detected[1] is True
    assert result.detected[5] is True

    for u in range(DEFAULT_CONFIG.NUM_SENSOR_UNITS):
        if u not in (1, 5):
            assert result.levels[u] == DistanceLevel.INF
            assert result.detected[u] is False


@pytest.mark.parametrize("seed", list(range(50)))
def test_paper_worked_example_holds_across_random_seeds(seed):
    detect_fns = _fixed_unit_detect_fns({1: 4, 5: 5})

    def signal_present_fn(u, round_index):
        if u == 1 and round_index == 0:
            return True
        if u == 5 and round_index == DEFAULT_CONFIG.ROUNDS_PER_PHASE1:
            return True
        return False

    rng = random.Random(seed)
    result = run_sensing_cycle(detect_fns, signal_present_fn, rng=rng)

    assert result.levels[1] == DistanceLevel.L4
    assert result.levels[5] == DistanceLevel.L5
    assert result.detected[1] is True
    assert result.detected[5] is True


def test_permanently_busy_unit_stays_unresolved_but_detected():
    n = DEFAULT_CONFIG.NUM_SENSOR_UNITS
    detect_fns = [make_ideal_detect_fn(LEVEL_TEST_DAC[4]) for _ in range(n)]

    def signal_present_fn(u, round_index):
        return u == 0  # unit 0 busy every single round, including phase 2

    rng = random.Random(1)
    result = run_sensing_cycle(detect_fns, signal_present_fn, rng=rng)

    assert result.levels[0] == DistanceLevel.INF
    assert result.detected[0] is True

    for u in range(1, n):
        assert result.levels[u] == DistanceLevel.L4


def test_no_signals_all_units_range_successfully():
    n = DEFAULT_CONFIG.NUM_SENSOR_UNITS
    detect_fns = [make_ideal_detect_fn(LEVEL_TEST_DAC[3]) for _ in range(n)]

    def signal_present_fn(u, round_index):
        return False

    rng = random.Random(7)
    result = run_sensing_cycle(detect_fns, signal_present_fn, rng=rng)

    assert all(level == DistanceLevel.L3 for level in result.levels)
    assert all(d is False for d in result.detected)


def test_phase2_only_detection_does_not_trigger_ranging():
    n = DEFAULT_CONFIG.NUM_SENSOR_UNITS
    detect_fns = [make_ideal_detect_fn(LEVEL_TEST_DAC[2]) for _ in range(n)]

    def signal_present_fn(u, round_index):
        return u == 3 and round_index == DEFAULT_CONFIG.ROUNDS_PER_PHASE1

    rng = random.Random(3)
    result = run_sensing_cycle(detect_fns, signal_present_fn, rng=rng)

    # unit 3 was free during all of Phase 1, so it should have still
    # resolved its own ranging successfully
    assert result.levels[3] == DistanceLevel.L2
    assert result.detected[3] is True