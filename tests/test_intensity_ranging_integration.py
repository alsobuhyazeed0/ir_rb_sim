import pytest

from ir_rb_sim.intensity import IntensityCurve
from ir_rb_sim.ranging import DistanceLevel, binary_search_range, make_ideal_detect_fn


def _resolve(distance_cm: float, offset_dac: float = 0.0) -> DistanceLevel:
    curve = IntensityCurve(unit_index=0, offset_dac=offset_dac)
    i_min = curve.i_min(distance_cm)
    return binary_search_range(make_ideal_detect_fn(i_min)).level


def test_close_distance_resolves_to_low_level():
    # very close object -> low DAC needed -> should resolve to an early level
    assert _resolve(2.0) in (DistanceLevel.L1, DistanceLevel.L2)


def test_far_distance_resolves_to_high_level_or_inf():
    # right at max range -> high DAC needed -> late level or INF
    assert _resolve(30.0) in (DistanceLevel.L7, DistanceLevel.INF)


def test_resolved_level_increases_monotonically_with_distance():
    distances = [2, 6, 10, 14, 18, 22, 26, 30]
    levels = [_resolve(d) for d in distances]

    # INF (=0 in the enum) sorts before L1 numerically, so compare using
    # a rank where INF is treated as "farthest", not "closest".
    def rank(level: DistanceLevel) -> int:
        return 99 if level == DistanceLevel.INF else level.value

    ranks = [rank(l) for l in levels]
    assert ranks == sorted(ranks)


def test_per_unit_offset_can_shift_resolved_level():
    distance_cm = 22.0
    level_no_offset = _resolve(distance_cm, offset_dac=0.0)
    level_big_offset = _resolve(distance_cm, offset_dac=200.0)  # much less sensitive unit
    assert level_big_offset != level_no_offset